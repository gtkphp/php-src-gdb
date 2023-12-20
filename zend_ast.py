#!/usr/bin/python

############################################################################
#
# Copyright (C) 2023 NoName.
# Contact: NoName
#
#
# GNU General Public License Usage
# Alternatively, this file may be used under the terms of the GNU
# General Public License version 3 as published by the Free Software
# Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
# included in the packaging of this file. Please review the following
# information to ensure the GNU General Public License requirements will
# be met: https://www.gnu.org/licenses/gpl-3.0.html.
#
############################################################################

import gdb
import sys
from dumper import *


import logging
#logging.basicConfig(filename='/home/dev/Documents/log.txt',level=logging.DEBUG)
#logging.debug('qdump__GHashTable .........................')



#zend_ast

zend_ast_kind_names = [
	"ZEND_AST_MAGIC_CONST",
	"ZEND_AST_TYPE",
	"ZEND_AST_CONSTANT_CLASS",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_ZVAL",
	"ZEND_AST_CONSTANT",
	"ZEND_AST_ZNODE",
	"ZEND_AST_FUNC_DECL",
	"ZEND_AST_CLOSURE",
	"ZEND_AST_METHOD",
	"ZEND_AST_CLASS",
	"ZEND_AST_ARROW_FUNC",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_ARG_LIST",
	"ZEND_AST_ARRAY",
	"ZEND_AST_ENCAPS_LIST",
	"ZEND_AST_EXPR_LIST",
	"ZEND_AST_STMT_LIST",
	"ZEND_AST_IF",
	"ZEND_AST_SWITCH_LIST",
	"ZEND_AST_CATCH_LIST",
	"ZEND_AST_PARAM_LIST",
	"ZEND_AST_CLOSURE_USES",
	"ZEND_AST_PROP_DECL",
	"ZEND_AST_CONST_DECL",
	"ZEND_AST_CLASS_CONST_DECL",
	"ZEND_AST_NAME_LIST",
	"ZEND_AST_TRAIT_ADAPTATIONS",
	"ZEND_AST_USE",
	"ZEND_AST_TYPE_UNION",
	"ZEND_AST_ATTRIBUTE_LIST",
	"ZEND_AST_ATTRIBUTE_GROUP",
	"ZEND_AST_MATCH_ARM_LIST",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_VAR",
	"ZEND_AST_CONST",
	"ZEND_AST_UNPACK",
	"ZEND_AST_UNARY_PLUS",
	"ZEND_AST_UNARY_MINUS",
	"ZEND_AST_CAST",
	"ZEND_AST_EMPTY",
	"ZEND_AST_ISSET",
	"ZEND_AST_SILENCE",
	"ZEND_AST_SHELL_EXEC",
	"ZEND_AST_CLONE",
	"ZEND_AST_EXIT",
	"ZEND_AST_PRINT",
	"ZEND_AST_INCLUDE_OR_EVAL",
	"ZEND_AST_UNARY_OP",
	"ZEND_AST_PRE_INC",
	"ZEND_AST_PRE_DEC",
	"ZEND_AST_POST_INC",
	"ZEND_AST_POST_DEC",
	"ZEND_AST_YIELD_FROM",
	"ZEND_AST_CLASS_NAME",
	"ZEND_AST_GLOBAL",
	"ZEND_AST_UNSET",
	"ZEND_AST_RETURN",
	"ZEND_AST_LABEL",
	"ZEND_AST_REF",
	"ZEND_AST_HALT_COMPILER",
	"ZEND_AST_ECHO",
	"ZEND_AST_THROW",
	"ZEND_AST_GOTO",
	"ZEND_AST_BREAK",
	"ZEND_AST_CONTINUE",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_DIM",
	"ZEND_AST_PROP",
	"ZEND_AST_NULLSAFE_PROP",
	"ZEND_AST_STATIC_PROP",
	"ZEND_AST_CALL",
	"ZEND_AST_CLASS_CONST",
	"ZEND_AST_ASSIGN",
	"ZEND_AST_ASSIGN_REF",
	"ZEND_AST_ASSIGN_OP",
	"ZEND_AST_BINARY_OP",
	"ZEND_AST_GREATER",
	"ZEND_AST_GREATER_EQUAL",
	"ZEND_AST_AND",
	"ZEND_AST_OR",
	"ZEND_AST_ARRAY_ELEM",
	"ZEND_AST_NEW",
	"ZEND_AST_INSTANCEOF",
	"ZEND_AST_YIELD",
	"ZEND_AST_COALESCE",
	"ZEND_AST_ASSIGN_COALESCE",
	"ZEND_AST_STATIC",
	"ZEND_AST_WHILE",
	"ZEND_AST_DO_WHILE",
	"ZEND_AST_IF_ELEM",
	"ZEND_AST_SWITCH",
	"ZEND_AST_SWITCH_CASE",
	"ZEND_AST_DECLARE",
	"ZEND_AST_USE_TRAIT",
	"ZEND_AST_TRAIT_PRECEDENCE",
	"ZEND_AST_METHOD_REFERENCE",
	"ZEND_AST_NAMESPACE",
	"ZEND_AST_USE_ELEM",
	"ZEND_AST_TRAIT_ALIAS",
	"ZEND_AST_GROUP_USE",
	"ZEND_AST_CLASS_CONST_GROUP",
	"ZEND_AST_ATTRIBUTE",
	"ZEND_AST_MATCH",
	"ZEND_AST_MATCH_ARM",
	"ZEND_AST_NAMED_ARG",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_METHOD_CALL",
	"ZEND_AST_NULLSAFE_METHOD_CALL",
	"ZEND_AST_STATIC_CALL",
	"ZEND_AST_CONDITIONAL",
	"ZEND_AST_TRY",
	"ZEND_AST_CATCH",
	"ZEND_AST_PROP_GROUP",
	"ZEND_AST_PROP_ELEM",
	"ZEND_AST_CONST_ELEM",
	"ZEND_AST_CONST_ENUM_INIT",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_FOR",
	"ZEND_AST_FOREACH",
	"ZEND_AST_ENUM_CASE",	"", 
"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
	"ZEND_AST_PARAM",
] 

zend_ast_attr_names = [
	"ZEND_NAME_FQ",
	"ZEND_NAME_NOT_FQ",
	"ZEND_NAME_RELATIVE"
]

def zend_ast_kind_name(kind):
	if kind>1280:
		return "<Optimized>"
	else:
		if zend_ast_kind_names[kind]=="":
			return "<Error>"
		else:
			return zend_ast_kind_names[kind]

def zend_ast_attr_name(attr):
	return zend_ast_attr_names[attr]


def qdump__zend_ast(d, value):
	val = int(value["kind"])
	kind = zend_ast_kind_name(val)
	num_child = -1
	if val>=64 and val<=66:
		valuetype = d.lookupType('zend_ast_zval')
		valuecast = value.cast(valuetype)
		d.putItem(valuecast)
	elif val>=67 and val<=71:
		valuetype = d.lookupType('zend_ast_decl')
		valuecast = value.cast(valuetype)
		d.putItem(valuecast)
	elif val>=128 and val<=147:
		valuetype = d.lookupType('zend_ast_list')
		valuecast = value.cast(valuetype)
		qdump__zend_ast_list(d, valuecast)
	else:
		if val>=0 and val<=3:
			num_child = 0
		elif val>=256 and val<=287:
			num_child = 1
		elif val>=512 and val<=550:
			num_child = 2
		elif val>=768 and val<=777:
			num_child = 3
		elif val>=1024 and val<=1027:
			num_child = 4
		elif val==1280:
			num_child = 5

		d.putNumChild(4)
		if d.isExpanded():
			with Children(d):
				with SubItem(d, 'kind'):
					d.putType("zend_ast_kind")
					d.putValue("%s (%d)" % (kind, val))
				with SubItem(d, 'attr'):
					d.putType("zend_ast_attr")
					d.putValue("%s (%d)" % (zend_ast_attr_name(int(value["attr"])), int(value["attr"])))
				with SubItem(d, 'lineno'):
					d.putItem(value["lineno"])
				if num_child>0:
					with SubItem(d, 'child'):
						size = num_child #int(value["children"])
						d.putItemCount(size)
						if d.isExpanded():
							#innerType = d.createType('zend_ast')
							innerType = d.lookupType('zend_ast').pointer()
							innerSize = d.ptrSize()#innerType.pointer().size()
							array = value["child"].address()#d.extractPointer(value["child"])
							with Children(d, size, maxNumChild=2000, childType=innerType):
								for i in d.childRange():
									p = array  + i * innerSize
									x = d.createValue(p, innerType)
									d.putSubItem(i, x)
				else:
					with SubItem(d, 'child'):
						d.putItem(value["child"])


def qdump__zend_ast_list(d, value):
	d.putType("zend_ast_list")
	d.putNumChild(4)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'kind'):
				d.putType("zend_ast_kind")
				name = zend_ast_kind_name(int(value["kind"]))
				d.putValue("%s (%d)" % (name, int(value["kind"])) )
			with SubItem(d, 'attr'):
				d.putType("zend_ast_attr")
				d.putValue(zend_ast_attr_name(int(value["attr"])))
			with SubItem(d, 'lineno'):
				d.putItem(value["lineno"])
			#with SubItem(d, 'child'):
			#	d.putItem(value["child"])
			with SubItem(d, 'child'):
				size = int(value["children"])
				d.putItemCount(size)
				if d.isExpanded():
					#innerType = d.createType('zend_ast')
					innerType = d.lookupType('zend_ast').pointer()
					innerSize = d.ptrSize()#innerType.pointer().size()
					array = value["child"].address()#d.extractPointer(value["child"])
					with Children(d, size, maxNumChild=2000, childType=innerType):
						for i in d.childRange():
							p = array  + i * innerSize
							x = d.createValue(p, innerType)
							d.putSubItem(i, x)
def qdump__zend_ast_decl(d, value):
	d.putType("zend_ast_decl")
	d.putNumChild(9)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'kind'):
				d.putType("zend_ast_kind")
				name = zend_ast_kind_name(int(value["kind"]))
				d.putValue("%s (%d)" % (name, int(value["kind"])) )
			with SubItem(d, 'attr'):
				d.putType("zend_ast_attr")
				d.putValue(zend_ast_attr_name(int(value["attr"])))
			with SubItem(d, 'start_lineno'):
				d.putItem(value["start_lineno"])
			with SubItem(d, 'end_lineno'):
				d.putItem(value["end_lineno"])
			with SubItem(d, 'flags'):
				d.putItem(value["flags"])
			with SubItem(d, 'lex_pos'):
				d.putItem(value["lex_pos"])
			with SubItem(d, 'doc_comment'):
				d.putItem(value["doc_comment"])
			with SubItem(d, 'name'):
				d.putItem(value["name"])
			with SubItem(d, 'child'):
				d.putItem(value["child"])
"""
				size = 5
				d.putItemCount(size)
				if d.isExpanded():
					innerType = d.createType('zend_ast')
					innerSize = d.ptrSize()#innerType.size()
					array = d.extractPointer(value["child"])
					with Children(d, size, maxNumChild=2000, childType=innerType):
						for i in d.childRange():
							p = array  + i * innerSize
							x = d.createValue(p, innerType)
							d.putSubItem(i, x)
"""


def qdump__zend_ast_zval(d, value):
	d.putType("zend_ast_zval")
	d.putNumChild(3)
	if d.isExpanded():
		with Children(d):
			with SubItem(d, 'kind'):
				d.putType("zend_ast_kind")
				name = zend_ast_kind_name(int(value["kind"]))
				d.putValue("%s (%d)" % (name, int(value["kind"])) )
			with SubItem(d, 'attr'):
				d.putType("zend_ast_attr")
				d.putValue(zend_ast_attr_name(int(value["attr"])))
			with SubItem(d, 'val'):
				valuetype = d.lookupType('zval')
				valuecast = value["val"].cast(valuetype)
				d.putItem(valuecast)
