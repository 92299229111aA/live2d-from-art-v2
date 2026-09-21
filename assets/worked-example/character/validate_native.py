from pathlib import Path
import ctypes as C,sys,json,os
library=os.environ.get('CUBISM_CORE_LIBRARY')
if not library:
 raise SystemExit('Set CUBISM_CORE_LIBRARY to your licensed Cubism Core dynamic library, or validate with Web Core.')
libpath=Path(library).expanduser()
lib=C.CDLL(str(libpath));lib.csmGetVersion.restype=C.c_uint
lib.csmHasMocConsistency.argtypes=[C.c_void_p,C.c_uint];lib.csmHasMocConsistency.restype=C.c_int
callback=C.CFUNCTYPE(None,C.c_char_p)(lambda msg: print(msg.decode(errors='replace')))
lib.csmSetLogFunction.argtypes=[C.c_void_p];lib.csmSetLogFunction(callback)
results=[]
for arg in sys.argv[1:] or [str(Path(__file__).parent/'runtime/Original.moc3')]:
 data=Path(arg).read_bytes();storage=C.create_string_buffer(len(data)+64);ptr=(C.addressof(storage)+63)&~63;C.memmove(ptr,data,len(data))
 ok=bool(lib.csmHasMocConsistency(ptr,len(data)))
 result={'file':str(Path(arg).resolve()),'nativeCoreVersion':lib.csmGetVersion(),'consistent':ok}
 if ok:
  lib.csmReviveMocInPlace.argtypes=[C.c_void_p,C.c_uint];lib.csmReviveMocInPlace.restype=C.c_void_p
  lib.csmGetSizeofModel.argtypes=[C.c_void_p];lib.csmGetSizeofModel.restype=C.c_uint
  lib.csmInitializeModelInPlace.argtypes=[C.c_void_p,C.c_void_p,C.c_uint];lib.csmInitializeModelInPlace.restype=C.c_void_p
  moc=lib.csmReviveMocInPlace(ptr,len(data));assert moc
  size=lib.csmGetSizeofModel(moc);model_storage=C.create_string_buffer(size+16);model_ptr=(C.addressof(model_storage)+15)&~15
  model=lib.csmInitializeModelInPlace(moc,model_ptr,size);assert model
  lib.csmUpdateModel.argtypes=[C.c_void_p];lib.csmUpdateModel(model)
  for name in ['Drawable','Parameter']:
   fn=getattr(lib,'csmGet'+name+'Count');fn.argtypes=[C.c_void_p];fn.restype=C.c_int;result[name.lower()+'Count']=fn(model)
  result['initializedAndUpdated']=True
 results.append(result);print(json.dumps(result))
if not sys.argv[1:]:Path(__file__).with_name('native-validation.json').write_text(json.dumps(results,indent=2))
sys.exit(0 if all(r['consistent'] for r in results) else 1)
