#!/usr/bin/python

import gdb
import sys
from dumper import *
#import os
#import platform

import logging
#logging.basicConfig(filename='/home/dev/Documents/log.txt',level=logging.DEBUG)
#logging.debug('qdump__GHashTable .........................')


# -----------------------------------------------------------------------------
# zend_val
# -----------------------------------------------------------------------------
def escape_string(str):
    return str.replace('"', '\\\"')

def quote(str):
    return "\\\"%s\\\"" % escape_string(str)


def zend_value_flags_to_string(type_info):
	flags = []
	type_collectable = (1<<4) & type_info
	type_protected = (1<<5) & type_info
	type_immutable = (1<<6) & type_info
	type_persistent = (1<<7) & type_info
	type_persistent_local = (1<<8) & type_info
	if type_collectable:
		flags.append("GC_NOT_COLLECTABLE")
	if type_protected:
		flags.append("GC_PROTECTED")
	if type_immutable:
		flags.append("GC_IMMUTABLE")
	if type_persistent:
		flags.append("GC_PERSISTENT")
	if type_persistent_local:
		flags.append("GC_PERSISTENT_LOCAL")
	return flags

def zend_value_flag_to_string(type_info, mask):
	type_collectable = (1<<4) & type_info
	type_protected = (1<<5) & type_info
	type_immutable = (1<<6) & type_info
	type_persistent = (1<<7) & type_info
	type_persistent_local = (1<<8) & type_info
	if type_collectable and mask==(1<<4):
		return "GC_NOT_COLLECTABLE"
	if type_protected and mask==(1<<5):
		return "GC_PROTECTED"
	if type_immutable and mask==(1<<6):
		return "GC_IMMUTABLE"
	if type_persistent and mask==(1<<7):
		return "GC_PERSISTENT"
	if type_persistent_local and mask==(1<<8):
		return "GC_PERSISTENT_LOCAL"
	return ""

def zend_value_flag_to_name(type_info, mask):
	type_collectable = (1<<4) & type_info
	type_protected = (1<<5) & type_info
	type_immutable = (1<<6) & type_info
	type_persistent = (1<<7) & type_info
	type_persistent_local = (1<<8) & type_info
	if type_collectable and mask==(1<<4):
		return "X"
	if type_protected and mask==(1<<5):
		return "X"
	if type_immutable and mask==(1<<6):
		return "X"
	if type_persistent and mask==(1<<7):
		return "X"
	if type_persistent_local and mask==(1<<8):
		return "X"
	return "_"

def zend_value_types_to_string(type_info):
	t_type = 0b00001111 & type_info

	if t_type==0x00:
		return "IS_UNDEF"
	elif t_type==0x01:
		return "IS_NULL"
	elif t_type==0x02:
		return "IS_FALSE"
	elif t_type==0x03:
		return "IS_TRUE"
	elif t_type==0x04:
		return "IS_LONG"
	elif t_type==0x05:
		return "IS_DOUBLE"
	elif t_type==0x06:
		return "IS_STRING"
	elif t_type==0x07:
		return "IS_ARRAY"
	elif t_type==0x08:
		return "IS_OBJECT"
	elif t_type==0x09:
		return "IS_RESOURCE"
	elif t_type==0x0A:
		return "IS_REFERENCE"
	elif t_type==0x0B:
		return "IS_CONSTANT_AST"

	return "IS_UNKNOWN"

def zend_value_types_to_php(type_info, value):
	t_type = 0b00001111 & type_info

	if t_type==0x00:
		return "undef"
	elif t_type==0x01:
		return "null"
	elif t_type==0x02:
		return "false"
	elif t_type==0x03:
		return "true"
	elif t_type==0x04:
		return "int"
	elif t_type==0x05:
		return "float"
	elif t_type==0x06:
		return "string"
	elif t_type==0x07:
		return "array"
	elif t_type==0x08:
		val = value['value']['obj']['ce']['name']['val']
		tt = gdb.lookup_type("char").pointer()
		ptr = val.address()
		str = gdb.Value(ptr).cast(tt)
		return str.string()
	elif t_type==0x09:
		return "resource"
	elif t_type==0x0A:
		return "reference"
	elif t_type==0x0B:
		return "constant_ast"

	elif t_type==0x0D:
		return "ptr"

	return "IS_UNKNOWN(%d)" % t_type

def zend_value_types_to_name(type_info):
	t_type = 0b00001111 & type_info

	if t_type==0x00:
		return "undef"
	elif t_type==0x01:
		return "nil"
	elif t_type==0x02:
		return "fval"
	elif t_type==0x03:
		return "tval"
	elif t_type==0x04:
		return "lval"
	elif t_type==0x05:
		return "dval"
	elif t_type==0x06:
		return "str"
	elif t_type==0x07:
		return "arr"
	elif t_type==0x08:
		return "obj"
	elif t_type==0x09:
		return "rsc"
	elif t_type==0x0A:
		return "ref"
	elif t_type==0x0B:
		return "ast"

	return "<UNKNOW>"


def zend_gc_infos_to_string(type_info):
	flags = []
	type_countable = (1<<0) & type_info
	type_collectable = (1<<1) & type_info
	if type_countable:
		flags.append("IS_TYPE_REFCOUNTED")
	if type_collectable:
		flags.append("IS_TYPE_COLLECTABLE")
	return flags

def zend_gc_flags_to_string(type_flags, flag):
	type_refcounted = (1<<0) & type_flags
	type_collectable = (1<<1) & type_flags
	if type_refcounted and flag==1:
		return "IS_TYPE_REFCOUNTED"
	elif type_collectable and flag==2:
		return "IS_TYPE_COLLECTABLE"
	else:
		return ""

def zend_gc_flags_to_bit(type_flags, flag):
	if type_flags & flag:
		return "X"
	else:
		return "_"


def zend_object_lookup_type(d, val):
	type_str = gdb.lookup_type("char").pointer()
	ptr = val.address()
	func_str = '%s_gdb_lookup_type()' % gdb.Value(ptr).cast(type_str).string()
	try:
		type_val = gdb.parse_and_eval(func_str)
		return type_val.string()
	except RuntimeError as error:
		if d.passExceptions:
			warn("Cannot evaluate '%s': %s" % (func_str, error))
		else:
			warn("Cannot evaluate: %s" % (error))
		return None
	return None

def zend_object_to_php_object(d, obj):
	val = obj['ce']['name']['val']
	tt = gdb.lookup_type("char").pointer()
	ptr = val.address()
	str = gdb.Value(ptr).cast(tt)
	class_name = zend_object_lookup_type(d, val)
	if class_name:
		offset = int(obj['handlers']['offset'])
		#eve = '(%s*)((void*)0x%x - sizeof(%s) + sizeof(zend_object))' % (class_name, obj.pointer(), class_name)
		eve = '(%s*)((void*)0x%x - (void*)0x%x)' % (class_name, obj.pointer(), offset)
		try:
			php_ptr = gdb.parse_and_eval(eve)
			type_obj = gdb.lookup_type(class_name).pointer()
			php_obj = gdb.Value(php_ptr).cast(type_obj)
			php_val = d.fromFrameValue(php_ptr)
			return php_val
		except RuntimeError as error:
			warn("Cannot evaluate %s: %s" % (eve, error))
			return obj
	else:
		return obj

def qdump__zval_ptr_zend_function_entry(d, value):
	type_info = int(value["u1"]["type_info"])
	type_info = int(value["u1"]["v"]["type"])
	d.putType("zval<%s>" % "zend_function_entry*")
	##tt = d.lookupType('zend_function_entry').pointer()
	#d.putAddress(ptr)
	#d.putItem(value["value"]["ptr"].cast(tt))
	##zfunc = value["value"]["ptr"].cast(tt)
	d.putValue("func name handler")
	d.putNumChild(1)
	logging.debug("putNumChild")
	if d.isExpanded():
		logging.debug("isExpanded")
		with Children(d):
			logging.debug("Children")
			with SubItem(d, 'value.ptr'):
				logging.debug("SubItem")
				d.putType("Helo")
				d.putValue("World")
				#const char *fname;
				#zif_handler handler;
				#const struct _zend_internal_arg_info *arg_info;
				#uint32_t num_args;
				#uint32_t flags;
				#d.putItem(value["value"]["ptr"])
				#logging.debug(zfunc)
			#with SubItem(d, 'u1'):
			#with SubItem(d, 'u2'):

def qdump_zval(d, value):
	# Get environment variables
	# export ZEND_GDB=gc,rtti,reflection all|ext
	# gc = garbage collector
	# rtti = run time type information
	# reflection = zend_object->ce
	#ZEND_GDB = os.getenv('ZEND_GDB') None ???
	#logging.debug(os.environ.items())
	#logging.debug(sys.version)#
	#logging.debug(platform.python_version())# 3.
	type_info = int(value["u1"]["type_info"])
	type_info = int(value["u1"]["v"]["type"])
	'''val = value["value"]["str"]["val"]'''
	'''tt = gdb.lookup_type("char").pointer()'''
	'''ptr = d.extractPointer(val)'''
	'''val = gdb.Value(ptr).cast(tt)'''
	'''if ztype>5 and ztype<12:'''
	'''	d.putValue("%d" % value["value.counted->gc.refcount"]["v"]["type"] )'''
	''' u1.v.type_info, u2, value.obj|str|dval '''
	d.putType("zval<%s>" % zend_value_types_to_php(type_info, value))
	'''d.putType("zval.%d" % type_info)'''
	'''if type_info>5 and type_info<12:
		d.putNumChild(0)'''
	if type_info==1:
		d.putNumChild(0)
	elif type_info==4:
		''' IS_LONG '''
		address = value.address()
		val = value["value"]["lval"]
		d.putValue("%d" % (val))
		d.putAddress(address)
	elif type_info==5:
		''' IS_DOUBLE '''
		address = value.address()
		val = value["value"]["dval"]
		d.putValue("%f" % val.floatingPoint())
		d.putAddress(address)
	elif type_info==6:
		''' IS_STRING '''
		tt = gdb.lookup_type("char").pointer()
		ptr = value["value"]["str"]["val"].address()
		val = gdb.Value(ptr).cast(tt)
		d.putType("zval<string>")
		d.putValue("%s" % quote(val.string()) )
		d.putNumChild(1)
		if d.isExpanded():
			with Children(d):
				with SubItem(d, 'u1.type_info'):
					type_flags = int(value["u1"]["v"]["type_flags"])
					flags = zend_gc_infos_to_string(type_flags)
					txt_flags = "|".join(flags)

					t = zend_value_types_to_string(type_info)
					v_type = int(value["u1"]["v"]["type"])
					
					u1_type_flags = [t] + flags
					u1_type_info = "|".join(u1_type_flags)
					
					u1_type_info = u1_type_info.replace("IS_STRING|IS_TYPE_REFCOUNTED", "IS_STRING_EX")
					u1_type_info = u1_type_info.replace("IS_ARRAY|IS_TYPE_REFCOUNTED|IS_TYPE_COLLECTABLE", "IS_ARRAY_EX")
					u1_type_info = u1_type_info.replace("IS_OBJECT|IS_TYPE_REFCOUNTED|IS_TYPE_COLLECTABLE", "IS_OBJECT_EX")
					u1_type_info = u1_type_info.replace("IS_RESOURCE|IS_TYPE_REFCOUNTED", "IS_RESOURCE_EX")
					u1_type_info = u1_type_info.replace("IS_REFERENCE|IS_TYPE_REFCOUNTED", "IS_REFERENCE_EX")
					u1_type_info = u1_type_info.replace("IS_CONSTANT_AST|IS_TYPE_REFCOUNTED", "IS_CONSTANT_AST_EX")

					d.putValue("%s (0x%.4X)" % ( u1_type_info, int(value["u1"]["type_info"])) )
					d.putType("union{uint32_t}")
					d.putNumChild(3)
					if d.isExpanded():
						with Children(d):
							with SubItem(d, 'type:8'):
								d.putValue("%s (0x%.2X)" % (t, v_type))
								d.putType("zend_value_types")
							with SubItem(d, 'type_flags:8'):
								d.putNumChild(2)
								d.putValue("%s (0x%.2X)" % (txt_flags, type_flags))
								with Children(d):
									with SubItem(d, "[%s]" % zend_gc_flags_to_bit(type_flags, 0x01)):
										bit = 1 if (type_flags&0x01) else 0
										d.putValue("%s (%d)" % (zend_gc_flags_to_string(type_flags, 0x01), bit ))
										d.putType("countable")
									with SubItem(d, "[%s]" % zend_gc_flags_to_bit(type_flags, 0x02)):
										bit = 1 if (type_flags&0x02) else 0
										d.putValue("%s (%d)" % (zend_gc_flags_to_string(type_flags, 0x02), bit ))
										d.putType("collectable")
							with SubItem(d, 'u.extra:16'):
								d.putValue("<Optimized>")
				with SubItem(d, 'u2'):
					d.putItem(value["u2"])
				with SubItem(d, 'value.str'):
					d.putItem(value["value"]["str"])
	elif type_info==7:
		''' IS_ARRAY '''
		value["value"]["arr"]
		d.putNumChild(1)
	elif type_info==8:
		''' IS_OBJECT '''
		d.putNumChild(3)
		if d.isExpanded():
			with Children(d):
				with SubItem(d, 'u1.type_info'):
					type_flags = int(value["u1"]["v"]["type_flags"])
					flags = zend_gc_infos_to_string(type_flags)
					txt_flags = "|".join(flags)

					t = zend_value_types_to_string(type_info)
					v_type = int(value["u1"]["v"]["type"])
					
					u1_type_flags = [t] + flags
					u1_type_info = "|".join(u1_type_flags)
					
					u1_type_info = u1_type_info.replace("IS_STRING|IS_TYPE_REFCOUNTED", "IS_STRING_EX")
					u1_type_info = u1_type_info.replace("IS_ARRAY|IS_TYPE_REFCOUNTED|IS_TYPE_COLLECTABLE", "IS_ARRAY_EX")
					u1_type_info = u1_type_info.replace("IS_OBJECT|IS_TYPE_REFCOUNTED|IS_TYPE_COLLECTABLE", "IS_OBJECT_EX")
					u1_type_info = u1_type_info.replace("IS_RESOURCE|IS_TYPE_REFCOUNTED", "IS_RESOURCE_EX")
					u1_type_info = u1_type_info.replace("IS_REFERENCE|IS_TYPE_REFCOUNTED", "IS_REFERENCE_EX")
					u1_type_info = u1_type_info.replace("IS_CONSTANT_AST|IS_TYPE_REFCOUNTED", "IS_CONSTANT_AST_EX")

					d.putValue("%s (0x%.4X)" % ( u1_type_info, int(value["u1"]["type_info"])) )
					d.putType("union{uint32_t}")
					d.putNumChild(3)
					if d.isExpanded():
						with Children(d):
							with SubItem(d, 'type:8'):
								d.putValue("%s (0x%.2X)" % (t, v_type))
								d.putType("zend_value_types")
							with SubItem(d, 'type_flags:8'):
								d.putNumChild(2)
								d.putValue("%s (0x%.2X)" % (txt_flags, type_flags))
								with Children(d):
									with SubItem(d, "[%s]" % zend_gc_flags_to_bit(type_flags, 0x01)):
										bit = 1 if (type_flags&0x01) else 0
										d.putValue("%s (%d)" % (zend_gc_flags_to_string(type_flags, 0x01), bit ))
										d.putType("countable")
									with SubItem(d, "[%s]" % zend_gc_flags_to_bit(type_flags, 0x02)):
										bit = 1 if (type_flags&0x02) else 0
										d.putValue("%s (%d)" % (zend_gc_flags_to_string(type_flags, 0x02), bit ))
										d.putType("collectable")
							with SubItem(d, 'u.extra:16'):
								d.putValue("<Optimized>")
				with SubItem(d, 'u2'):
					d.putItem(value["u2"])
				with SubItem(d, "value.%s<-%s" % (zend_value_types_to_name(type_info), zend_object_lookup_type(d, value["value"]["obj"]['ce']['name']['val'])) ):
					d.putItem(zend_object_to_php_object(d, value["value"]["obj"]))
					#d.putItem(value["value"]["obj"])
	elif type_info==10:
		''' IS_REFERENCE '''
		d.putNumChild(1)
		if d.isExpanded():
			with Children(d):
				'''
				addr = value["value"]["ref"]["val"].address()
				typeObj = d.lookupType('zval').pointer()
				valuecast = d.createValue(addr, typeObj)

				with SubItem(d, 'value.ref.val'):
					qdump__zval(d, valuecast.dereference())
				'''
				#d.putSubItem('value.ref.val', valuecast)

				typeObj = d.lookupType('zval')
				val = value["value"]["ref"]["val"].cast(typeObj)
				#d.putSubItem('value.ref.val', val)
				with SubItem(d, 'value.ref.val'):
					qdump_zval(d, val)
	elif type_info==13:
		''' IS_PTR '''
		d.putNumChild(1)
		with Children(d):
			with SubItem(d, 'ptr'):
				d.putValue("undefined")
				d.putType("void*")

	else:
		d.putNumChild(0)


def qdump__zval(d, value):
	qdump_zval(d, value)

def qdump___zval(d, value):
	qdump_zval(d, value)


'''
def qdump__struct_zval_struct(d, value):
	logging.debug("qdump___zval_struct")
	qdump__zval(d, value)

def qdump__zval_struct(d, value):
	logging.debug("qdump __zval_struct")
	qdump__zval(d, value)

def qdump__struct__zval_struct(d, value):
	logging.debug("qdump __zval_struct")
	qdump__zval(d, value)
def qdump___zval_struct(d, value):
	logging.debug("qdump __zval_struct")
	qdump__zval(d, value)
'''

def qdump__zend_refcounted_h(d, value):
	d.putType("zend_gc_ref_trait")
	d.putNumChild(1)
	ref_count = value["refcount"]
	type_info = int(value["u"]["type_info"])

	t_info = (0b00011111<<4) & type_info

	'''d.putValue('@0x%x' % value.address() )'''
	d.putAddress(value.address())

	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'ref_count'):
				d.putItem(ref_count)
			with SubItem(d, 'u.type_info'):
				d.putNumChild(2)
				t = zend_value_types_to_string(type_info)
				flags = [t] + zend_value_flags_to_string(type_info)
				txt_flags = "|".join(flags)
				txt_flags = txt_flags.replace("IS_NULL|GC_NOT_COLLECTABLE", "GC_NULL")
				txt_flags = txt_flags.replace("IS_STRING|GC_NOT_COLLECTABLE", "GC_STRING")
				txt_flags = txt_flags.replace("IS_ARRAY", "GC_ARRAY")
				txt_flags = txt_flags.replace("IS_OBJECT", "GC_OBJECT")
				txt_flags = txt_flags.replace("IS_RESOURCE|GC_NOT_COLLECTABLE", "GC_RESOURCE")
				txt_flags = txt_flags.replace("IS_REFERENCE|GC_NOT_COLLECTABLE", "GC_REFERENCE")
				txt_flags = txt_flags.replace("IS_CONSTANT_AST|GC_NOT_COLLECTABLE", "GC_CONSTANT_AST")
				d.putValue("%s" % txt_flags)
				d.putType("zend_gc_flags")
				if d.isExpanded():
					with Children(d):
						''' type:4 '''
						with SubItem(d, 'type:4'):
							d.putNumChild(0)
							d.putValue(zend_value_types_to_string(type_info))
							d.putType("zend_value_types")
						''' flags:5 '''
						with SubItem(d, 'flags:5'):
							d.putNumChild(5)
							d.putType("zend_gc_flags")
							flags = zend_value_flags_to_string(type_info)
							d.putValue("%s" % "|".join(flags))
							if d.isExpanded():
								with Children(d):
									with SubItem(d, "[%s]" % zend_value_flag_to_name(type_info, 1<<4)):
										d.putValue("%s" % zend_value_flag_to_string(type_info, 1<<4))
										d.putType("collectable")
									with SubItem(d, "[%s]" % zend_value_flag_to_name(type_info, 1<<5)):
										d.putValue("%s" % zend_value_flag_to_string(type_info, 1<<5))
										d.putType("protected")
									with SubItem(d, "[%s]" % zend_value_flag_to_name(type_info, 1<<6)):
										d.putValue("%s" % zend_value_flag_to_string(type_info, 1<<6))
										d.putType("immutable")
									with SubItem(d, "[%s]" % zend_value_flag_to_name(type_info, 1<<7)):
										d.putValue("%s" % zend_value_flag_to_string(type_info, 1<<7))
										d.putType("persistent")
									with SubItem(d, "[%s]" % zend_value_flag_to_name(type_info, 1<<8)):
										d.putValue("%s" % zend_value_flag_to_string(type_info, 1<<8))
										d.putType("persistent_local")


def qdump___zend_refcounted_h(d, value):
	qdump__zend_refcounted_h(d, value)

''' gc_root_buffer '''
def qdump__gc_stack(d, value):
	d.putItem(value)

def qdump___gc_stack(d, value):
	qdump__gc_stack(d, value)



def qdump__zend_string(d, value):
	tt = gdb.lookup_type("char").pointer()
	ptr = value["val"].address()
	val = gdb.Value(ptr).cast(tt)
	d.putType("zend_string")
	d.putValue("%s" % quote(val.string()) )
	d.putNumChild(2)
	if d.isExpanded():
		'''d.putValue("@%x" % value.address )'''
		'''d.putValue("@%p" % value.address() )'''
		'''with Children(d):
			d.putSubItem("gc", value["gc"])
			d.putSubItem("len", value["len"])
			d.putSubItem("val", value["val"])'''
		with Children(d):
			with SubItem(d, 'gc'):
				qdump__zend_refcounted_h(d, value["gc"])
			with SubItem(d, 'val'):
				d.putType("char[%d]" % value["len"].integer())
				d.putValue("%s" % quote(val.string()) )

# -----------------------------------------------------------------------------
# Bucket
# -----------------------------------------------------------------------------

class q__Bucket:
	"Prints a Bucket"

	class _iterator:
		def __init__(self, ht, keyname, valuekey):
			self.ht = ht["arData"]
			self.keyname = keyname
			self.valuekey = valuekey
			self.size = 0
			self.pos = 0
			if ht != 0:
				self.size = int(ht["nNumOfElements"])

		def __iter__(self):
			return self

		def next(self):
			if self.ht == 0:
				raise StopIteration
			while int(self.pos) < int(self.size):
				key = self.ht[self.pos][self.keyname]
				val = self.ht[self.pos]["val"]
				self.pos = self.pos + 1
				if self.keyname == "h":
					str_key = "%d" % int(key)
				else:
					tt = gdb.lookup_type("char").pointer()
					ptr = key["val"].address()
					str_k = gdb.Value(ptr).cast(tt)
					str_key = "%s" % quote(str_k.string())
				return (str_key, val)
			raise StopIteration

		__next__ = next

	def __init__ (self, value, keyname, valuekey):
		self.value = value
		self.keyname = keyname
		self.valuekey = valuekey

	def children(self):
		return self._iterator(self.value, self.keyname, self.valuekey)

	def to_string (self):
		return  "0x%x" % (long(self.value))

	def display_hint (self):
		return "map"

'''
	if $ht->u.v.flags & 4
		printf "Packed"
	else
		printf "Hash"
	end
'''

'''
def dump_HashTable(d, value, keyname, type, ptrtype):
	return
'''


def qdump__Bucket_function(d, value):
	d.putType("Hello")
	d.putValue("World")

	tt = gdb.lookup_type("char").pointer()
	ptr = value["key"]["val"].address()
	#val = gdb.Value(ptr).cast(tt)
	# quote(val.string())

	logging.debug(ptr)

def qdump__zval_function(d, value):
	#vtype = d.lookupType('zend_function').pointer()
	#vv = value["value"]["ptr"].cast(vtype)
	#tt = gdb.lookup_type("char").pointer()
	#ptr = vv["internal_function"]["function_name"]["val"].address()
	#vvv = gdb.Value(ptr).cast(tt)
	#logging.debug(vvv.string())

	valuetype = d.lookupType('zend_function').pointer()
	valuecast = value["value"]["ptr"].cast(valuetype)

	internalvalue = valuecast["internal_function"]
	
	internaltype = d.lookupType('zend_internal_function')
	internalcast = internalvalue.cast(internaltype)
	logging.debug(internalcast["handler"])

	d.putType("zval<ptr>")
	#d.putValue("handler name")
	d.putNumChild(1)
	#if d.isExpanded():
	with Children(d):
		d.putSubItem('value.ptr', internalcast)
		#with SubItem(d, 'value.ptr'):
			#d.putItem(valuecast)
			##d.putValue("undefined")
			##d.putType("void***")

def qdump__zend_array_function(d, value):
	#dump_HashTable(d, value, 'key', 3, d.lookupType('zend_function_entry').pointer())
	d.putType("zend_array<zend_string*, zval>")
	keyname = "key"
	valuetype = d.lookupType('zval_function')# zval
	bucket = q__Bucket(value, keyname, valuetype)
	myiter = iter(bucket.children())
	k, v = next(myiter)

	#vtype = d.lookupType('zend_function').pointer()
	#vv = v["value"]["ptr"].cast(vtype)
	#tt = gdb.lookup_type("char").pointer()
	#ptr = vv["internal_function"]["function_name"]["val"].address()
	#vvv = gdb.Value(ptr).cast(tt)
	#logging.debug(vvv.string())

	#d.putAdress(value.adress())
	d.putNumChild(10)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'arData'):
				d.putItemCount(int(value["nNumOfElements"]))
				d.putType('Bucket [%d]' % int(value["nTableSize"]))
				d.putNumChild(value["nNumOfElements"])
				if d.isExpanded():
					with Children(d):
						i = 0
						for item in bucket.children():
							#d.putSubItem("[%s]" % k, v.cast(valuetype)) can't Expand
							d.putSubItem("[%d]" % i, v.cast(valuetype))
							i += 1
			with SubItem(d, 'gc'):
				qdump__zend_refcounted_h(d, value["gc"])
			with SubItem(d, 'nInternalPointer'):
				d.putItem(value["nInternalPointer"])
			with SubItem(d, 'nNextFreeElement'):
				d.putItem(value["nNextFreeElement"])
			with SubItem(d, 'nNumOfElements'):
				d.putItem(value["nNumOfElements"])
			with SubItem(d, 'nNumUsed'):
				d.putItem(value["nNumUsed"])
			with SubItem(d, 'nTableMask'):
				d.putItem(value["nTableMask"])
			with SubItem(d, 'nTableSize'):
				d.putItem(value["nTableSize"])
			with SubItem(d, 'pDestructor'):
				d.putItem(value["pDestructor"])
			with SubItem(d, 'u'):
				d.putItem(value["u"])

def qdump__zend_array_zval(d, value):
	d.putType("zend_array<zend_ulong, zval>")
	keyname = "h"
	#d.putAdress(value.adress())
	d.putNumChild(10)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'arData'):
				d.putItemCount(int(value["nNumOfElements"]))
				d.putType('Bucket')
				d.putNumChild(value["nNumOfElements"])
				if d.isExpanded():
					with Children(d):
						keytype = d.lookupType('zend_ulong')
						valuetype = d.lookupType('zval')
						bucket = q__Bucket(value, keyname, valuetype)
						for item in bucket.children():
							#with SubItem(d, '[%s]' % item[0]):
							#	with Children(d):
							#		d.putValue(item[1].cast(valuetype))
							d.putSubItem("[%s]" % item[0], item[1].cast(valuetype))
			with SubItem(d, 'gc'):
				qdump__zend_refcounted_h(d, value["gc"])
			with SubItem(d, 'nInternalPointer'):
				d.putItem(value["nInternalPointer"])
			with SubItem(d, 'nNextFreeElement'):
				d.putItem(value["nNextFreeElement"])
			with SubItem(d, 'nNumOfElements'):
				d.putItem(value["nNumOfElements"])
			with SubItem(d, 'nNumUsed'):
				d.putItem(value["nNumUsed"])
			with SubItem(d, 'nTableMask'):
				d.putItem(value["nTableMask"])
			with SubItem(d, 'nTableSize'):
				d.putItem(value["nTableSize"])
			with SubItem(d, 'pDestructor'):
				d.putItem(value["pDestructor"])
			with SubItem(d, 'u'):
				d.putItem(value["u"])


def zend_check_flag(bit):
	if bit:
		return "X"
	else:
		return "_"



_ZEND_TYPE_EXTRA_FLAGS_SHIFT = 25
_ZEND_SEND_MODE_SHIFT = _ZEND_TYPE_EXTRA_FLAGS_SHIFT
_ZEND_IS_REFERENCE_BIT = (1 << (_ZEND_TYPE_EXTRA_FLAGS_SHIFT + 0))
_ZEND_IS_VARIADIC_BIT = (1 << (_ZEND_TYPE_EXTRA_FLAGS_SHIFT + 2))
_ZEND_IS_PROMOTED_BIT = (1 << (_ZEND_TYPE_EXTRA_FLAGS_SHIFT + 3))
_ZEND_IS_TENTATIVE_BIT = (1 << (_ZEND_TYPE_EXTRA_FLAGS_SHIFT + 4))


_ZEND_TYPE_MASK = 0x1ffffff

_ZEND_TYPE_NAME_BIT = 0x1000000
_ZEND_TYPE_CE_BIT = 0x800000
_ZEND_TYPE_LIST_BIT = 0x400000

_ZEND_TYPE_ARENA_BIT = 0x100000
_ZEND_TYPE_NULLABLE_BIT = 0x2

IS_UNDEF = 0
IS_NULL = 1
IS_FALSE = 2
IS_TRUE = 3
IS_LONG = 4
IS_DOUBLE = 5
IS_STRING = 6
IS_ARRAY = 7
IS_OBJECT = 8
IS_RESOURCE = 9
IS_REFERENCE = 10
IS_CONSTANT_AST = 11

PHP_TYPE_MASK = 0x07FFFF


def zend_type_flags_to_string(type_mask, flag):
	if flag == _ZEND_IS_REFERENCE_BIT:
		return "_ZEND_IS_REFERENCE_BIT (%d)" % (1 if type_mask & _ZEND_IS_REFERENCE_BIT else 0)
	elif flag == _ZEND_IS_VARIADIC_BIT:
		return "_ZEND_IS_VARIADIC_BIT (%d)" % (1 if type_mask & _ZEND_IS_VARIADIC_BIT else 0)
	elif flag == _ZEND_IS_PROMOTED_BIT:
		return "_ZEND_IS_PROMOTED_BIT (%d)" %  (1 if type_mask & _ZEND_IS_PROMOTED_BIT else 0)
	elif flag == _ZEND_IS_TENTATIVE_BIT:
		return "_ZEND_IS_TENTATIVE_BIT (%d)" %  (1 if type_mask & _ZEND_IS_TENTATIVE_BIT else 0)
	else:
		type_mask = type_mask & _ZEND_TYPE_MASK

		type_name = type_mask & _ZEND_TYPE_NAME_BIT
		type_ce = type_mask & _ZEND_TYPE_CE_BIT
		type_list = type_mask & _ZEND_TYPE_LIST_BIT
		type_nullable = type_mask & _ZEND_TYPE_NULLABLE_BIT

		if flag == _ZEND_TYPE_NAME_BIT:
			return "_ZEND_TYPE_NAME_BIT (%d)" % (1 if type_name else 0)
		elif flag == _ZEND_TYPE_CE_BIT:
			return "_ZEND_TYPE_CE_BIT (%d)" % (1 if type_ce else 0)
		elif flag == _ZEND_TYPE_LIST_BIT:
			return "_ZEND_TYPE_LIST_BIT (%d)" % (1 if type_list else 0)
		elif flag == _ZEND_TYPE_NULLABLE_BIT:
			return "_ZEND_TYPE_NULLABLE_BIT (%d)" % (1 if type_nullable else 0)
		else:
			t_type = PHP_TYPE_MASK & type_mask # 0b01111111111111111111

			if flag == IS_UNDEF:
				return "IS_UNDEF (%d)" % (1 if t_type==(0<<IS_UNDEF) else 0)
			elif flag == IS_NULL:
				return "IS_NULL (%d)" % (1 if t_type==(1<<IS_NULL) else 0)
			elif flag==IS_FALSE:
				return "IS_FALSE (%d)" % (1 if t_type==(1<<IS_FALSE) else 0)
			elif flag==IS_TRUE:
				return "IS_TRUE (%d)" % (1 if t_type==(1<<IS_TRUE) else 0)
			elif flag==IS_LONG:
				return "IS_LONG (%d)" % (1 if t_type==(1<<IS_LONG) else 0)
			elif flag==IS_DOUBLE:
				return "IS_DOUBLE (%d)" % (1 if t_type==(1<<IS_DOUBLE) else 0)
			elif flag==IS_STRING:
				return "IS_STRING (%d)" % (1 if t_type==(1<<IS_STRING) else 0)
			elif flag==IS_ARRAY:
				return "IS_ARRAY (%d)" % (1 if t_type==(1<<IS_ARRAY) else 0)
			elif flag==IS_OBJECT:
				return "IS_OBJECT (%d)" % (1 if t_type==(1<<IS_OBJECT) else 0)
			elif flag==IS_RESOURCE:
				return "IS_RESOURCE (%d)" % (1 if t_type==(1<<IS_RESOURCE) else 0)
			elif flag==IS_REFERENCE:
				return "IS_REFERENCE (%d)" % (1 if t_type==(1<<IS_REFERENCE) else 0)
			elif flag==IS_CONSTANT_AST:
				return "IS_CONSTANT_AST (%d)" % (1 if t_type==(1<<IS_CONSTANT_AST) else 0)
			else:
				return "{?}"

def qdump__zend_type_ptr(d, value):
	type_mask = int(value["type_mask"]) & _ZEND_TYPE_MASK
	if type_mask & _ZEND_TYPE_NAME_BIT:
		tt = d.lookupType('zend_string').pointer()
		d.putItem(value["ptr"].cast(tt))
	elif type_mask & _ZEND_TYPE_CE_BIT:
		return
	elif type_mask & _ZEND_TYPE_LIST_BIT:
		return
	elif type_mask & _ZEND_TYPE_NULLABLE_BIT:
		return
	else:
		return

def zend_arg_info_get_name(value):
	tt = gdb.lookup_type("char").pointer()
	ptr = value["name"]["val"].address()
	val = gdb.Value(ptr).cast(tt)
	return val.string()

def zend_type_ptr_to_string(d, value):
	tt = d.lookupType('zend_string').pointer()
	str = value.cast(tt)
	tt = gdb.lookup_type("char").pointer()
	ptr = str["val"].address()
	val = gdb.Value(ptr).cast(tt)
	return val.string()

"""
def zend_arg_info_get_default_value(value):
	tt = gdb.lookup_type("char").pointer()
	ptr = value["default_value"]["val"].address()
	val = gdb.Value(ptr).cast(tt)
	return val.string()
"""

def zend_arg_info_to_string(d, value):
	type_mask = int(value["type"]["type_mask"]) & _ZEND_TYPE_MASK
	if type_mask & _ZEND_TYPE_NAME_BIT:
		return "%s $%s" % (zend_type_ptr_to_string(d, value["type"]["ptr"]), zend_arg_info_get_name(value))
	elif type_mask & _ZEND_TYPE_CE_BIT:
		return "..."
	elif type_mask & _ZEND_TYPE_LIST_BIT:
		return "..."
	elif type_mask & _ZEND_TYPE_NULLABLE_BIT:
		return "..."
	else:
		t_type = PHP_TYPE_MASK & int(value["type"]["type_mask"])
		if t_type==0x00:
			return "undef"
		elif t_type==(1<<IS_NULL):
			return "null"
		elif t_type==(1<<IS_FALSE):
			#return "bool $%s = false" % zend_arg_info_get_name(value)
			return "bool"
		elif t_type==(1<<IS_TRUE):
			#return "bool $%s = true" % zend_arg_info_get_name(value)
			return "bool"
		elif t_type==(1<<IS_LONG):
			#return "int $%s = ..." % zend_arg_info_get_name(value)
			return "int $%s" % zend_arg_info_get_name(value)
		elif t_type==(1<<IS_DOUBLE):
			return "float"
		elif t_type==(1<<IS_STRING):
			return "string"
		elif t_type==(1<<IS_ARRAY):
			return "array"
		elif t_type==(1<<IS_OBJECT):
			return "object"
		elif t_type==(1<<IS_RESOURCE):
			return "resource"
		elif t_type==(1<<IS_REFERENCE):
			return "reference"
		else:
			return "mixed"


def qdump__zend_type(d, value):
	type_mask = int(value["type_mask"])
	d.putType("zend_type")
	#d.putValue("%s" % zend_type_to_string(value))
	d.putNumChild(2)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'ptr'):
				#d.putItem(value["ptr"])
				qdump__zend_type_ptr(d, value)
			with SubItem(d, 'type_mask'):
				d.putType("unsigned int:24")
				d.putNumChild(17)
				#d.putValue("%s (0x%.2X)" % (txt_flags, type_mask))
				d.putValue("%d" % type_mask)
				if d.isExpanded():
					with Children(d):
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_IS_REFERENCE_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_IS_REFERENCE_BIT) )
							d.putType("pass_by_reference:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_IS_VARIADIC_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_IS_VARIADIC_BIT) )
							d.putType("variadic:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_IS_PROMOTED_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_IS_PROMOTED_BIT) )
							d.putType("promoted:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_IS_TENTATIVE_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_IS_TENTATIVE_BIT) )
							d.putType("tentative:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_TYPE_NAME_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_TYPE_NAME_BIT) )
							d.putType("name:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_TYPE_CE_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_TYPE_CE_BIT) )
							d.putType("ce:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_TYPE_LIST_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_TYPE_LIST_BIT) )
							d.putType("list:1")
						with SubItem(d, "[%s]" % zend_check_flag(type_mask&_ZEND_TYPE_NULLABLE_BIT)):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, _ZEND_TYPE_NULLABLE_BIT) )
							d.putType("nullable:1")

						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_UNDEF))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_UNDEF) )
							d.putType("undef:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_NULL))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_NULL) )
							d.putType("null:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_FALSE))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_FALSE) )
							d.putType("false:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_TRUE))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_TRUE) )
							d.putType("true:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_LONG))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_LONG) )
							d.putType("long:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_DOUBLE))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_DOUBLE) )
							d.putType("double:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_STRING))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_STRING) )
							d.putType("string:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_ARRAY))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_ARRAY) )
							d.putType("array:1")
						with SubItem(d, "[%s]" % zend_check_flag((type_mask&PHP_TYPE_MASK)&(1<<IS_OBJECT))):
							d.putValue("%s" % zend_type_flags_to_string(type_mask, IS_OBJECT) )
							d.putType("object:1")
						#IS_RESOURCE = 9
						#IS_REFERENCE = 10
						#IS_CONSTANT_AST = 11


def qdump__zend_arg_info(d, value):
	d.putType("zend_arg_info")
	d.putValue("%s" % zend_arg_info_to_string(d, value))
	#d.putValue("...")
	d.putNumChild(3)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'name'):
				d.putItem(value["name"])
			with SubItem(d, 'type'):
				qdump__zend_type(d, value["type"])
			with SubItem(d, 'default_value'):
				d.putItem(value["default_value"])


def zend_op_code_to_string(d, value):
	func_str = 'zend_get_opcode_name(%d)' % int(value)
	try:
		type_val = gdb.parse_and_eval(func_str)
		return type_val.string()
	except RuntimeError as error:
		if d.passExceptions:
			warn("Cannot evaluate '%s': %s" % (func_str, error))
		else:
			warn("Cannot evaluate: %s" % (error))
		return None
	return None

IS_UNUSED	= 0
IS_CONST	= (1<<0)
IS_TMP_VAR	= (1<<1)
IS_VAR		= (1<<2)
IS_CV		= (1<<3)

def zend_op_code_type_to_string(d, value):
	if value==IS_UNUSED:
		return "UNUSED"
	elif value==IS_CONST:
		return "CONST"
	elif value==IS_TMP_VAR:
		return "TMP_VAR"
	elif value==IS_VAR:
		return "VAR"
	elif value==IS_CV:
		return "CV"
	else:
		return None

"""
/* Used for result.type of smart branch instructions */
#define IS_SMART_BRANCH_JMPZ  (1<<4)
#define IS_SMART_BRANCH_JMPNZ (1<<5)
znode_op
"""

def qdump__zend_op_code(d, value):
	d.putType("zend_uchar")
	d.putValue("%s (%d)" % (zend_op_code_to_string(d, value), int(value)))
	d.putNumChild(0)

def qdump__zend_op(d, value):
	d.putType("zend_op")
	d.putValue("%s" % zend_op_code_to_string(d, value["opcode"]).replace('ZEND_', '') )
	d.putNumChild(10)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'handler'):
				d.putItem(value["handler"])
			with SubItem(d, 'op1'):
				d.putItem(value["op1"])
			with SubItem(d, 'op2'):
				d.putItem(value["op2"])
			with SubItem(d, 'result'):
				d.putItem(value["result"])
			with SubItem(d, 'extended_value'):
				d.putItem(value["extended_value"])
			with SubItem(d, 'lineno'):
				d.putItem(value["lineno"])
			with SubItem(d, 'opcode'):
				#d.putItem(value["opcode"])
				qdump__zend_op_code(d, value["opcode"])
			with SubItem(d, 'op1_type'):
				d.putValue( zend_op_code_type_to_string(d, int(value["op1_type"])) )
				#d.putItem(value["op1_type"])
			with SubItem(d, 'op2_type'):
				d.putValue( zend_op_code_type_to_string(d, int(value["op2_type"])) )
				#d.putItem(value["op2_type"])
			with SubItem(d, 'result_type'):
				d.putValue( zend_op_code_type_to_string(d, int(value["result_type"])) )
				#d.putItem(value["result_type"])



def qdump__zend_op_array(d, value):
	d.putType("zend_op_array")
	d.putNumChild(32)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'type'):
				d.putItem(value["type"])
			with SubItem(d, 'arg_flags'):
				d.putItem(value["arg_flags"])
			with SubItem(d, 'fn_flags'):
				d.putItem(value["fn_flags"])
			with SubItem(d, 'function_name'):
				d.putItem(value["function_name"])
			with SubItem(d, 'prototype'):
				d.putItem(value["prototype"])
			with SubItem(d, 'num_args'):
				d.putItem(value["num_args"])
			with SubItem(d, 'required_num_args'):
				d.putItem(value["required_num_args"])
			with SubItem(d, 'arg_info'):
				d.putItem(value["arg_info"])
			with SubItem(d, 'attributes'):
				d.putItem(value["attributes"])
			with SubItem(d, 'cache_size'):
				d.putItem(value["cache_size"])
			with SubItem(d, 'last_var'):
				d.putItem(value["last_var"])
			with SubItem(d, 'T'):
				d.putItem(value["T"])
			with SubItem(d, 'last'):
				d.putItem(value["last"])
			with SubItem(d, 'opcodes'):
				size = int(value["last"])
				d.putItemCount(size)
				if d.isExpanded():
					innerType = d.createType('zend_op')
					innerSize = innerType.size()
					array = d.extractPointer(value["opcodes"])
					with Children(d, size, maxNumChild=2000, childType=innerType):
						for i in d.childRange():
							p = array  + i * innerSize
							x = d.createValue(p, innerType)
							d.putSubItem(i, x)
				"""
				d.putItem(value["opcodes"])
				#see in /usr/shar/Qtcreator/debugger def qdumpHelper_QList() for array of pointer
				"""
			with SubItem(d, 'run_time_cache__ptr'):
				d.putItem(value["run_time_cache__ptr"])
			with SubItem(d, 'static_variables_ptr__ptr'):
				d.putItem(value["static_variables_ptr__ptr"])
			with SubItem(d, 'static_variables'):
				d.putItem(value["static_variables"])
			with SubItem(d, 'vars'):
				d.putItem(value["vars"])
			with SubItem(d, 'refcount'):
				d.putItem(value["refcount"])
			with SubItem(d, 'last_live_range'):
				d.putItem(value["last_live_range"])
			with SubItem(d, 'last_try_catch'):
				d.putItem(value["last_try_catch"])
			with SubItem(d, 'live_range'):
				d.putItem(value["live_range"])
			with SubItem(d, 'try_catch_array'):
				d.putItem(value["try_catch_array"])
			with SubItem(d, 'filename'):
				d.putItem(value["filename"])
			with SubItem(d, 'line_start'):
				d.putItem(value["line_start"])
			with SubItem(d, 'line_end'):
				d.putItem(value["line_end"])
			with SubItem(d, 'doc_comment'):
				d.putItem(value["doc_comment"])
			with SubItem(d, 'last_literal'):
				d.putItem(value["last_literal"])
			with SubItem(d, 'num_dynamic_func_defs'):
				d.putItem(value["num_dynamic_func_defs"])
			with SubItem(d, 'literals'):
				d.putItem(value["literals"])
			with SubItem(d, 'dynamic_func_defs'):
				d.putItem(value["dynamic_func_defs"])
			with SubItem(d, 'reserved'):
				d.putItem(value["reserved"])




"""
https://www.npopov.com/2017/04/14/PHP-7-Virtual-machine.html
def qdump__zend_execute_data(d, value):

"""
