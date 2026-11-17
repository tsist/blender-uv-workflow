"""Run with Blender --background --factory-startup --python <this file>."""
import bpy,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from uv_workflow_addon import core
from uv_workflow_addon.packing import pack
from uv_workflow_addon.metrics import measure

def run_case(label,width,height,scale,locked=False,partial=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m=bpy.data.meshes.new('fixture')
    vertices=[];faces=[];values=[]
    # Three independent rectangles, equal pixel aspect and 2:1 area budgets.
    for i,(x,y,w,h) in enumerate([(80,80,160,120),(450,80,320,120),(80,350,160,120)]):
        j=len(vertices);vertices.extend([(i*3,0,0),(i*3+1,0,0),(i*3+1,1,0),(i*3,1,0)])
        faces.append([j,j+1,j+2,j+3]);values.extend([[x/width,y/height],[(x+w)/width,y/height],[(x+w)/width,(y+h)/height],[x/width,(y+h)/height]])
    m.from_pydata(vertices,[],faces);m.uv_layers.new(name='UV')
    o=bpy.data.objects.new('fixture',m);bpy.context.collection.objects.link(o)
    uv=np.array(values,dtype=np.float32);core._write_uv(m,'UV',uv)
    held=list(range(4)) if locked else []
    cs={'fixed':{str(i):uv[i].tolist() for i in held}}
    fs=[1,2] if partial else [0,1,2]
    solved,details=pack([o],'UV',{'fixture':uv},{'fixture':fs},{'fixture':cs},{'rotate':True,'scale':scale},width,height,8,16)
    result=solved['fixture'];core._write_uv(m,'UV',result)
    q=measure(core.measurement_input([o],'UV',1),width,height,2000000)
    # Unselected pinned faces are excluded from native selection, not obstacles.
    if not partial:assert q['status']=='pass' and q['gap']['min_px']>=16 and q['boundary_margin_px']>=8,(label,q)
    moving_gap=None
    if partial:
        rows=core.measurement_input([o],'UV',1)
        rows[0]['triangles']=rows[0]['triangles'][2:];rows[0]['uv']=rows[0]['uv'][2:];rows[0]['islands']=rows[0]['islands'][2:]
        moving=measure(rows,width,height,2000000);moving_gap=moving['gap']['min_px']
        assert 16<=moving_gap<19,(label,moving_gap)
        assert q['status']=='fail' and q['overlap']['positive_pairs']>0,label
    if locked or partial:assert np.array_equal(result[:4],uv[:4]),label
    if not scale:
        for f in fs:
            ids=faces[f];old=uv[ids].astype(float)*[width,height];new=result[ids].astype(float)*[width,height]
            assert np.allclose(np.linalg.norm(old[:,None]-old[None,:],axis=2),np.linalg.norm(new[:,None]-new[None,:],axis=2),rtol=0,atol=.001),label
    elif not locked:
        assert 16<=q['gap']['min_px']<19,(label,q['gap'])
    return {'case':label,'gap_px':q['gap']['min_px'],'moving_selected_gap_px':moving_gap,'border_px':q['boundary_margin_px'],'status':q['status'],'protected_exact':True,'scale':scale,'details':details}

results=[run_case('free-fit-square',2048,2048,True),run_case('free-density-square',2048,2048,False),run_case('locked-square',2048,2048,False,True),run_case('free-fit-rectangle',2048,1024,True),run_case('free-fit-portrait',1024,2048,True),run_case('locked-rectangle',2048,1024,False,True),run_case('partial-unselected-exact',2048,2048,False,False,True)]
out={'version':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'cases':results,'status':'pass'}
target=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else None
if target:target.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out),flush=True)
