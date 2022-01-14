import sys
import io
import xml.etree.ElementTree as ET

# Order is important
EXT_VENDORS = [
  'ARB',
  'KHR',
  'EXT',
  'NV',
  'AMD',
  'ATI',
  'APPLE'
]

WGL_UNICODE = [
  'wglUseFontBitmaps',
  'wglUseFontOutlines',
]

WGL_HOOKS = [
  'wglMakeCurrent',
  'wglMakeContextCurrentARB',
  'wglMakeContextCurrentEXT',
  'wglMakeAssociatedContextCurrentAMD'
]

GUARDS = {
  'gl': '1',
  'wgl': 'defined(_WIN32)'
}

def generate_file(src_path, dst_path, data):
  t = open(src_path, 'r', newline='')
  template_data = t.read()
  t.close()
  [head, tail] = template_data.split('%GENERATED%', 1)
  o = open(dst_path, 'w', newline='')
  o.write(head)
  o.write(data.getvalue())
  o.write(tail)
  o.close()

class FeatureSet:
  def __init__(self, version_min):
    self.version_min = version_min
    self.extensions = set()
    self.enums = []
    self.funcs = []

  def dup(self):
    d = FeatureSet(self.version_min)
    d.extensions = self.extensions.copy()
    return d

class GLEnum:
  def __init__(self, name, value):
    self.name = name
    self.value = value
    self.feature_set = None

class GLFunctionParam:
  def __init__(self, name, type):
    self.name = name
    self.type = type

  def c_decl(self):
    return self.type + " " + self.name

class GLFunction:
  def __init__(self, name, return_type):
    self.name = name
    self.return_type = return_type
    self.params = []
    self.feature_set = None

  def add_param(self, name, type):
    self.params.append(GLFunctionParam(name, type))

  def c_decl(self):
    return "GLAPI %-20s RESIN_APIENTRY %s%s(%s);\n" % (self.return_type, 'resin_impl_', self.name, self.args())

  def c_pfn(self):
    return "typedef %s (RESIN_APIENTRY *%s)(%s);\n" % (self.return_type, self.pfn(), self.args())

  def pfn(self):
    return "PFN%sPROC" % self.name.upper()

  def cpp_define(self):
    return "#define %-40s %s%s\n" % (self.name, 'resin_impl_', self.name)

  def args(self):
    if self.params:
      return ", ".join(map(lambda x: x.c_decl(), self.params))
    return "void"

  def argnames(self):
    return ", ".join(map(lambda x: x.name, self.params))

class Builder:
  def __init__(self, api):
    self.api = api
    self.enums = []
    self.enums_by_name = {}
    self.funcs = []
    self.funcs_by_name = {}
    self.feature_sets = []
    self.out = io.StringIO(newline='')

  def parse_enums(self, spec):
    for e in spec.findall("./enums/enum"):
      attr = e.attrib
      name = attr['name']
      value = attr['value']
      enum = GLEnum(name, value)
      self.enums.append(enum)
      self.enums_by_name[enum.name] = enum

  def parse_functions(self, spec):
    for cmd in spec.findall("./commands/command"):
      proto = "".join(cmd.find('./proto').itertext())
      [proto_type, proto_name] = proto.replace('*', '* ').rsplit(None, 1)
      proto_type = proto_type.replace(' *', '*')
      if not self.is_valid_func(proto_name):
        continue
      fun = GLFunction(proto_name, proto_type)
      params = cmd.findall('./param')
      for p in params:
        raw = "".join(p.itertext())
        [type, name] = raw.replace('*', '* ').rsplit(None, 1)
        type = type.replace(' *', '*')
        fun.add_param(name, type)
      self.funcs.append(fun)
      self.funcs_by_name[fun.name] = fun

  def parse_feature_sets(self, spec):
    for f in spec.findall("./feature"):
      if f.attrib['api'] != self.api:
        continue
      version_str = f.attrib['number']
      version = int(version_str[0] + version_str[2])
      fs = FeatureSet(version)
      for e in f.findall('./require/enum'):
        enum = self.enums_by_name[e.attrib['name']]
        if enum.feature_set == None:
          fs.enums.append(enum)
          enum.feature_set = fs
      for c in f.findall('./require/command'):
        name = c.attrib['name']
        if not self.is_valid_func(name):
          continue
        func = self.funcs_by_name[name]
        if func.feature_set == None:
          fs.funcs.append(func)
          func.feature_set = fs
      self.feature_sets.append(fs)

  def parse_extensions(self, spec):
    for ext in spec.findall('./extensions/extension'):
      apis = ext.attrib['supported'].split('|')
      if not self.api in apis:
        continue
      ext_name = ext.attrib['name']
      for e in ext.findall('./require/enum'):
        enum = self.enums_by_name[e.attrib['name']]
        fs = None
        if enum.feature_set != None:
          fs = self.make_feature_set(enum.feature_set.version_min, set.union(enum.feature_set.extensions, {ext_name}))
          enum.feature_set.enums.remove(enum)
        else:
          fs = self.make_feature_set(None, {ext_name})
        fs.enums.append(enum)
        enum.feature_set = fs
      for cmd in ext.findall('./require/command'):
        func = self.funcs_by_name[cmd.attrib['name']]
        fs = None
        if func.feature_set != None:
          fs = self.make_feature_set(func.feature_set.version_min, set.union(func.feature_set.extensions, {ext_name}))
          func.feature_set.funcs.remove(func)
        else:
          fs = self.make_feature_set(None, {ext_name})
        fs.funcs.append(func)
        func.feature_set = fs


  def parse(self, xml_dir):
    src = "%s/%s.xml" % (xml_dir, self.api)
    spec = ET.parse(src)
    self.parse_enums(spec)
    self.parse_functions(spec)
    self.parse_feature_sets(spec)
    self.parse_extensions(spec)
    self.funcs = list(filter(lambda x: x.feature_set, self.funcs))


  def make_feature_set(self, version_min, extensions):
    for fs in self.feature_sets:
      if fs.version_min == version_min and fs.extensions == extensions:
        return fs
    fs = FeatureSet(version_min)
    fs.extensions = extensions.copy()
    self.feature_sets.append(fs)
    return fs

  def gen_enum(self, enum):
    self.out.write("#define %-60s %s\n" % (enum.name, enum.value))

  def gen_feature_set(self, fs):
    version_major = None
    version_minor = None
    check = None
    if fs.version_min:
      version_major = fs.version_min // 10
      version_minor = fs.version_min % 10
      check = not ((version_major == 1) and (version_minor == 0))
    if check:
      self.out.write("#if (RESIN_GL_VERSION >= %d)\n" % fs.version_min)
    if version_major and fs.extensions == set():
      self.out.write("#define %s_VERSION_%d_%d 1\n" % (self.api.upper(), version_major, version_minor))
    self.out.write("\n")
    for e in fs.enums:
      self.gen_enum(e)
    self.out.write("\n")
    for f in fs.funcs:
      self.out.write(f.cpp_define())
    self.out.write("\n")
    if fs.funcs:
      self.out.write("#ifdef RESIN_PROCS\n")
      for f in fs.funcs:
        self.out.write(f.c_pfn())
      self.out.write("#endif\n")
    if check:
      self.out.write("#endif\n\n")

  def gen_decls(self):
    for f in self.funcs:
      self.out.write(f.c_decl())

  def gen(self):
    self.feature_sets.sort(key=lambda x: (x.version_min * 10 if x.version_min else 10000) + (0 if x.extensions == set() else 1))
    for fs in self.feature_sets:
      self.gen_feature_set(fs)
    self.gen_decls()

  def output(self, template_dir, out_dir):
    template = "%s/%s.h.in" % (template_dir, self.api)
    dst = "%s/%s.h" % (out_dir, self.api)
    self.gen()
    generate_file(template, dst, self.out)

  def is_valid_func(self, name):
    return name.startswith(self.api) and not name in WGL_UNICODE

class CodeGen:
  def __init__(self):
    self.gl = Builder('gl')
    self.wgl = Builder('wgl')
    self.apis = [self.gl, self.wgl]

  def parse(self, xml_dir):
    for a in self.apis:
      a.parse(xml_dir)

  def output_headers(self, template_dir, out_dir):
    for a in self.apis:
      a.output(template_dir, out_dir)

  def output_loader_generic_api(self, api, out):
    out.write("#if %s\n" % GUARDS[api.api])
    for f in api.funcs:
      out.write("static %s RESIN_APIENTRY resin_loader_%s(%s);\n" % (f.return_type, f.name, f.args()))
    out.write("\n")
    for f in api.funcs:
      out.write("static %s resin_ptr_%s = &resin_loader_%s;\n" % (f.pfn(), f.name, f.name))
    out.write("\n")
    for f in api.funcs:
      out.write("static %s RESIN_APIENTRY resin_loader_%s(%s)\n" % (f.return_type, f.name, f.args()))
      out.write("{\n")
      out.write("    resin_ptr_%s = (%s)resinGetProcAddr(\"%s\");\n" % (f.name, f.pfn(), f.name))
      out.write("    %sresin_ptr_%s(%s);\n" % ("return " if f.return_type.lower() != "void" else "", f.name, f.argnames()))
      out.write("}\n")
      out.write("\n")
    out.write("\n")
    for f in api.funcs:
      out.write("%s RESIN_APIENTRY resin_%s_%s(%s)\n" % (f.return_type, "impl2" if f.name in WGL_HOOKS else "impl", f.name, f.args()))
      out.write("{\n")
      out.write("    %sresin_ptr_%s(%s);\n" % ("return " if f.return_type.lower() != "void" else "", f.name, f.argnames()))
      out.write("}\n")
      out.write("\n")
    out.write("#endif\n\n")

  def output_loader_generic_reset(self, out):
    out.write("RESIN_API void resinReset(void)\n")
    out.write("{\n")
    out.write("#if defined(_WIN32)\n")
    for f in self.gl.funcs:
      out.write("    resin_ptr_%s = &resin_loader_%s;\n" % (f.name, f.name))
    out.write("#endif\n")
    out.write("}\n\n")

  def output_loader_generic(self, template_dir, out_dir):
    out = io.StringIO(newline='')
    for a in self.apis:
      self.output_loader_generic_api(a, out)
    self.output_loader_generic_reset(out)
    template = "%s/loader_generic.c.in" % template_dir
    out_file = "%s/loader_generic.c" % out_dir
    generate_file(template, out_file, out)

template_dir = sys.argv[1]
xml_dir = sys.argv[2]
out_include_dir = sys.argv[3]
out_src_dir = sys.argv[4]

cg = CodeGen()
cg.parse(xml_dir)
cg.output_headers(template_dir, out_include_dir)
cg.output_loader_generic(template_dir, out_src_dir)
