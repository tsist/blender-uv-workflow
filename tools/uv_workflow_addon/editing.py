"""Explicit local edits of a managed candidate, with exact rollback/protection."""
import copy
import numpy as np
from . import core
from .contract import fail


def selected_loops(obj, layer, selection):
    """Resolve stable face seeds; no positional island numbering is accepted."""
    m=obj.data;ids=selection['indices'];domain=selection['domain']
    limit=len(m.loops) if domain=='LOOPS' else len(m.polygons)
    if any(i>=limit for i in ids):fail('Selection index out of range: '+obj.name)
    if domain=='LOOPS':return sorted(ids),[]
    faces=set(ids)
    if domain=='ISLANDS':
        groups,_=core.islands(obj,layer);seeds={groups[i] for i in ids}
        faces={i for i,g in enumerate(groups) if g in seeds}
    return sorted({i for f in faces for i in m.polygons[f].loop_indices}),sorted(faces)


def _pin_write(mesh,layer,indices):
    uv=mesh.uv_layers[layer]
    if indices and not len(uv.pin):uv.data[indices[0]].pin_uv=True
    if len(uv.pin):
        flags=np.zeros(len(mesh.loops),dtype=bool);flags[indices]=True
        mesh.uv_layers[layer].pin.foreach_set('value',flags)
    mesh.update()


def _sync_pins(obj, uv, constraints, indices, native):
    """Import only an explicit selected scope; locked faces retain authority."""
    chosen=set(indices);actual=set(native);old=constraints['fixed']
    locked={i for f in constraints['locked_faces'] for i in obj.data.polygons[f].loop_indices}
    if (actual ^ set(map(int,old))) - chosen:
        fail('Native pin changes outside synchronization selection: '+obj.name,'CONFLICT')
    if locked-actual:
        fail('Locked faces must remain pinned; restore their native pins before synchronization: '+obj.name,'CONFLICT')
    for i in locked:
        if not np.array_equal(uv[i],np.asarray(old[str(i)],dtype=np.float32)):
            fail('Synchronization cannot move a locked-face anchor: '+obj.name+'/'+str(i),'CONFLICT')
    previous=set(constraints['pins'])
    pins=(previous-chosen)|((actual & chosen)-locked)|(previous & chosen & locked)
    constraints['pins']=sorted(pins)
    fixed=pins|locked
    if fixed!=actual:fail('Synchronization would rewrite native pins: '+obj.name,'CONFLICT')
    constraints['fixed']={str(i):(uv[i].tolist() if i in chosen-locked else old[str(i)]) for i in sorted(fixed)}
    reanchored=[i for i in sorted(chosen & fixed-locked) if str(i) in old and old[str(i)]!=uv[i].tolist()]
    return {'kind':'sync_pins','scope_loops':len(chosen),'added_pins':sorted(pins-previous),
            'removed_pins':sorted(previous-pins),'reanchored_pins':reanchored,
            'locked_corners_preserved':len(locked),'native_flags':'unchanged','coordinates':'unchanged'}


def _chain(obj,uv,indices):
    """One open UV edge chain; every alias of a chosen UV vertex is explicit."""
    m=obj.data;nodes={};loop_nodes={};selected=set(indices)
    for loop in m.loops:
        key=(loop.vertex_index,float(uv[loop.index,0]),float(uv[loop.index,1]))
        nodes.setdefault(key,[]).append(loop.index);loop_nodes[loop.index]=key
    chosen={loop_nodes[i] for i in indices}
    if len(chosen)<3:fail('Straighten requires at least three UV vertices')
    if any(not set(nodes[k])<=selected for k in chosen):
        fail('Straighten selection must include all corners of each chosen UV vertex')
    links={k:set() for k in chosen}
    for face in m.polygons:
        ls=list(face.loop_indices)
        for a,b in zip(ls,ls[1:]+ls[:1]):
            ka,kb=loop_nodes[a],loop_nodes[b]
            if ka in chosen and kb in chosen and ka!=kb:
                links[ka].add(kb);links[kb].add(ka)
    ends=[k for k in chosen if len(links[k])==1]
    if len(ends)!=2 or any(len(v) not in (1,2) for v in links.values()):
        fail('Straighten requires one unbranched open UV edge chain')
    order=[];previous=None;node=min(ends,key=lambda k:min(nodes[k]))
    while node is not None:
        order.append(node)
        options=links[node]-({previous} if previous is not None else set())
        previous,node=node,next(iter(options),None)
        if node in order:fail('Straighten chain is cyclic')
    if len(order)!=len(chosen):fail('Straighten selection contains disconnected chains')
    return [min(nodes[k]) for k in order],[nodes[k] for k in order]


def _density(obj,layer,uv,faces,action,width,height,unit):
    from .editing_math import apply_coordinates
    m=obj.data;m.calc_loop_triangles();groups,_=core.islands(obj,layer)
    selected_groups={groups[f] for f in faces};out=uv.copy();rows=[]
    world=np.array([list(obj.matrix_world@v.co) for v in m.vertices])*unit
    for group in sorted(selected_groups):
        tris=[t for t in m.loop_triangles if groups[t.polygon_index]==group]
        loops=sorted({i for t in tris for i in t.loops})
        if not tris or not loops:fail('Selected island has no measurable triangles')
        pos=world[np.array([list(t.vertices) for t in tris])]
        area=float(np.linalg.norm(np.cross(pos[:,1]-pos[:,0],pos[:,2]-pos[:,0]),axis=1).sum()/2)
        pixel=uv[np.array([list(t.loops) for t in tris])].astype(float)*[width,height]
        a,b=pixel[:,1]-pixel[:,0],pixel[:,2]-pixel[:,0]
        pa=float(np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0]).sum()/2)
        if not np.isfinite(area+pa) or min(area,pa)<=0:fail('Density requires valid nonzero world and UV area','VALIDATION_FAILED')
        density=np.sqrt(pa/area);factor=action['target_px_m']/density
        out,_=apply_coordinates(out,loops,{'kind':'scale','factors':[float(factor)]*2},width,height)
        rows.append({'face_seed':min(t.polygon_index for t in tris),'before_px_m':float(density),'scale':float(factor)})
    return out,{'kind':'density','islands':rows}


def edit_candidate(scene,objects,record,s,v,unit,progress):
    from .editing_math import apply_coordinates
    layer=record['layer'];cid=v['candidate'];action=v['action'];kind=action['kind']
    current={o.name:core._uv_fingerprint(o.data,layer) for o in objects}
    if current!=record['uv_hash']:fail('Native edits require revalidation before local editing','CONFLICT')
    # validate reports manual pin conflicts but does not rewrite hard constraints.
    # Never silently discard such pins when a later edit rewrites managed flags.
    for o,c in zip(objects,record['constraints']):
        if set(core._pins(o.data,layer))!=set(map(int,c['fixed'])):
            if kind!='sync_pins' or o.name not in v['selection']:
                fail('Native pins differ from managed constraints: '+o.name+'; explicitly synchronize selected native pins','CONFLICT')
    binding=v.get('selection_binding')
    if binding and any(binding['geometry'][n]!=record['geometry'][n] or binding['uv_hash'][n]!=current[n] for n in v['selection']):
        fail('Captured selection is stale; capture the selection again','CONFLICT')
    adopted=s.get('adopted')
    if adopted and adopted['candidate']==cid:
        if any(core._hash([e.index for e in o.data.edges if e.use_seam])!=adopted['applied_seams'].get(o.name) for o in objects):
            fail('Native seam edits require revalidation before local editing','CONFLICT')
    # All coordinate work and fixed-point checks finish before the first write.
    before=core.protection(objects,excluded=(layer,));old_state=scene.get(core.STATE)
    old_uv={o.name:core.coordinates(o.data,layer) for o in objects}
    old_pins={o.name:core._pins(o.data,layer) for o in objects}
    old_seams={o.name:[e.index for e in o.data.edges if e.use_seam] for o in objects}
    edited=copy.deepcopy(record);cs=edited['constraints'];check=dict(record['manifest'])
    if 'pair_budget' in v:check['pair_budget']=v['pair_budget']
    width,height=check['width'],check['height'];outputs={};details={};scopes={}
    packed=None
    if kind in ('stack','unstack'):
        from .island_tools import stack,unstack
        from .policies import defaults
        from .recipes import binding as recipe_binding
        settings=edited.setdefault('settings',defaults(recipe_binding(objects,check,unit)))
        if settings['mode']=='TILED':fail('Atlas stack/unstack requires EXCLUSIVE settings; tiled repetition is a separate intent','CONFLICT')
        if kind=='stack':
            if any(g['id']==action['group_id'] for g in settings['reuse_groups']):fail('Reuse group id already exists','CONFLICT')
            packed,details,declaration=stack(objects,layer,old_uv,v['selection'],action,width,height)
            settings['reuse_groups'].append({'id':action['group_id'],'members':declaration['members']})
        else:
            packed,details=unstack(objects,layer,old_uv,v['selection'],action['offset_px'],width,height)
            moved={n:set(selected_loops(next(o for o in objects if o.name==n),layer,row)[1]) for n,row in v['selection'].items()}
            groups=[]
            for g in settings['reuse_groups']:
                members=[m for m in g['members'] if not set(m['faces'])&moved.get(m['object'],set())]
                if len(members)>1:groups.append({**g,'members':members})
            settings['reuse_groups']=groups
        from .policies import normalize as normalize_settings
        edited['settings']=normalize_settings(settings,[o.name for o in objects])
    if kind=='pack':
        from .packing import pack_with_reuse
        face_scopes={o.name:selected_loops(o,layer,v['selection'][o.name])[1] for o in objects if o.name in v['selection']}
        policy=record.get('recipe',{}).get('policy',{})
        if edited.get('settings',{}).get('mode')=='TILED':fail('TILED uses density/orientation and repetition, not atlas pack','CONFLICT')
        packed,details=pack_with_reuse(objects,layer,old_uv,face_scopes,{o.name:c for o,c in zip(objects,cs)},action,
            width,height,policy.get('border_px_min',check['border_px']),policy.get('gap_px_min',check['margin_px']),edited.get('settings'))
    for o,c in zip(objects,cs):
        uv=old_uv[o.name];out=uv.copy();row=v['selection'].get(o.name)
        if row is None:
            outputs[o.name]=out;scopes[o.name]=[];continue
        indices,faces=selected_loops(o,layer,row);scopes[o.name]=indices
        if not indices:fail('Empty resolved UV selection: '+o.name)
        if kind in ('pin','lock'):
            field='pins' if kind=='pin' else 'locked_faces';chosen=indices if kind=='pin' else faces
            existing=set(c[field]);c[field]=sorted(existing|set(chosen) if action['enabled'] else existing-set(chosen))
            fixed=set(c['pins'])
            for f in c['locked_faces']:fixed.update(o.data.polygons[f].loop_indices)
            # Existing anchors remain authoritative, including outside selection.
            # Reanchoring manually moved pins is a separate explicit operation.
            c['fixed']={str(i):c['fixed'].get(str(i),uv[i].tolist()) for i in sorted(fixed)}
            details[o.name]={'kind':kind,'enabled':action['enabled'],'selected_count':len(chosen)}
        elif kind=='sync_pins':details[o.name]=_sync_pins(o,uv,c,indices,old_pins[o.name])
        elif kind=='split':
            from .splitting import split
            out,details[o.name]=split(o,uv,faces,action['delta_px'],width,height)
        elif kind in ('pack','stack','unstack'):out=packed[o.name]
        elif kind=='orient':
            from .island_tools import orient
            out,details[o.name]=orient(o,uv,faces,action['edge_loops'],action['angle_degrees'],width,height)
        elif kind=='stitch':
            from .stitching import stitch
            out,details[o.name]=stitch(o,uv,indices,action['pairs'][o.name],action['limit_px'],width,height)
        elif kind in ('relax','unwrap'):
            from .local_solver import solve
            plan=record.get('seam_plan',record['metrics']['seams']).get(o.name,[])
            out,details[o.name]=solve(o,layer,uv,faces,c,plan,action,width,height)
        elif kind=='density':out,details[o.name]=_density(o,layer,uv,faces,action,width,height,unit)
        elif kind=='straighten':
            chain,aliases=_chain(o,uv,indices)
            out,details[o.name]=apply_coordinates(uv,chain,action,width,height)
            for representative,ls in zip(chain,aliases):out[ls]=out[representative]
        else:out,details[o.name]=apply_coordinates(uv,indices,action,width,height)
        untouched=np.ones(len(uv),dtype=bool);untouched[indices]=False
        if not np.array_equal(out[untouched],uv[untouched]):fail('Edit moved unselected UV','VALIDATION_FAILED')
        for i,value in c['fixed'].items():
            if not np.array_equal(out[int(i)],np.asarray(value,dtype=np.float32)):
                fail('Edit would move a pinned or locked UV: '+o.name+'/'+i,'CONFLICT')
        outputs[o.name]=out
    progress('local_edit',action=kind)
    try:
        for o,c in zip(objects,cs):
            core._write_uv(o.data,layer,outputs[o.name]);_pin_write(o.data,layer,sorted(map(int,c['fixed'])))
        if core.protection(objects,excluded=(layer,))!=before:fail('Original data protection mismatch','VALIDATION_FAILED')
        quality=core._quality(objects,layer,check,cs,unit,progress,edited.get('recipe'),edited.get('settings'))
        if quality['constraints']['status']!='pass':fail('Edit violates seam or fixed constraints: '+str(quality['constraints']['violations'][:8]),'CONFLICT')
        edited['metrics']=quality;edited['uv_hash']={o.name:core._uv_fingerprint(o.data,layer) for o in objects}
        edited['status']='needs_review' if quality['status']=='pass' else quality['status']
        edited['revision']=int(record.get('revision',0))+1
        edited['last_edit']={'action':copy.deepcopy(action),'selection':copy.deepcopy(v['selection']),
            'details':details,'previous_uv_hash':current,'unselected_uv':'exact','old_layers':'unchanged'}
        # Preserve deliberately captured seam flags and add newly separated edges.
        previous_plan=record.get('seam_plan',record['metrics']['seams'])
        edited['seam_plan']={o.name:sorted(set(previous_plan.get(o.name,[]))|
            (set(quality['seams'][o.name])-set(record['metrics']['seams'][o.name]))) for o in objects}
        if kind=='stitch' and action['seam_mode']=='CLEAR_JOINED':
            for o in objects:
                joined=set(details.get(o.name,{}).get('joined_edges',[]))
                remaining=set(quality['seams'][o.name])
                edited['seam_plan'][o.name]=sorted(set(edited['seam_plan'][o.name])-(joined-remaining))
        if adopted and adopted['candidate']==cid:
            for o in objects:
                cuts=set(edited['seam_plan'][o.name])
                for e in o.data.edges:e.use_seam=e.index in cuts
            s['adopted']['applied_seams']={n:core._hash(edges) for n,edges in edited['seam_plan'].items()}
        s['candidates'][cid]=edited;core._store(scene,s)
        return {'status':'candidate_edited','candidate':cid,'record':edited,'quality_acceptance':'requires_visual_and_purpose_review'}
    except Exception:
        for o in objects:
            core._write_uv(o.data,layer,old_uv[o.name]);_pin_write(o.data,layer,old_pins[o.name])
            seams=set(old_seams[o.name])
            for e in o.data.edges:e.use_seam=e.index in seams
        if old_state is None:
            if core.STATE in scene:del scene[core.STATE]
        else:scene[core.STATE]=old_state
        raise
