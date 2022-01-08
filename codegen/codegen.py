import sys
import io
import xml.etree.ElementTree as ET

class FeatureSet:
  def __init__(self, version_min):
    self.version_min = version_min
    self.enums = []
    self.funcs = []

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
    return ("GLAPI %-20s RESIN_APIENTRY %s%s(%s);\n" % (self.return_type, 'resin_impl_', self.name, ", ".join(map(lambda x: x.c_decl(), self.params))))

  def c_pfn(self):
    return "typedef %s (RESIN_APIENTRY *PFN%sPROC)(%s);\n" % (self.return_type, self.name.upper(), ", ".join(map(lambda x: x.c_decl(), self.params)))

  def cpp_define(self):
    return "#define %s %s%s\n" % (self.name, 'resin_impl_', self.name)

class Builder:
  def __init__(self):
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
      if f.attrib['api'] != 'gl':
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
        func = self.funcs_by_name[c.attrib['name']]
        if func.feature_set == None:
          fs.funcs.append(func)
          func.feature_set = fs
      self.feature_sets.append(fs)

  def parse(self, src):
    spec = ET.parse(src)
    self.parse_enums(spec)
    self.parse_functions(spec)
    self.parse_feature_sets(spec)

  def gen_enum(self, enum):
    self.out.write("#define %-60s %s\n" % (enum.name, enum.value))

  def gen_feature_set(self, fs):
    version_major = int(fs.version_min / 10)
    version_minor = int(fs.version_min % 10)

    self.out.write(f"/* OpenGL {version_major}.{version_minor} */\n")
    self.out.write(f"#if (RESIN_GL_VERSION >= {fs.version_min})\n")
    self.out.write(f"#define GL_VERSION_{version_major}_{version_minor} 1\n")
    self.out.write("\n")
    for e in fs.enums:
      self.gen_enum(e)
    self.out.write("\n")
    for f in fs.funcs:
      self.out.write(f.cpp_define())
    self.out.write("\n")
    self.out.write("#ifdef RESIN_PROCS\n")
    for f in fs.funcs:
      self.out.write(f.c_pfn())
    self.out.write("#endif\n")
    self.out.write("#endif\n\n")

  def gen_decls(self):
    for f in self.funcs:
      self.out.write(f.c_decl())

  def gen(self):
    for fs in self.feature_sets:
      self.gen_feature_set(fs)
    self.gen_decls()

  def output(self, template, dst):
    t = open(template, 'r', newline='')
    template_data = t.read()
    t.close()
    [head, tail] = template_data.split('%GENERATED%', 1)
    o = open(dst, 'w', newline='')
    o.write(head)
    o.write(self.out.getvalue())
    o.write(tail)
    o.close()

  def run(self, template, src, dst):
    self.parse(src)
    self.gen()
    self.output(template, dst)


template = sys.argv[1]
src = sys.argv[2]
dst = sys.argv[3]

builder = Builder()
builder.run(template, src, dst)
