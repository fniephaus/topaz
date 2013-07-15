from topaz.objects.objectobject import W_Object
from topaz.module import ClassDef
from topaz.modules.ffi.type import W_TypeObject
from topaz.modules.ffi.dynamic_library import W_DL_SymbolObject
from topaz.modules.ffi.pointer import W_PointerObject
from topaz.error import RubyError
from topaz.coerce import Coerce
from topaz.objects.functionobject import W_BuiltinFunction

from rpython.rtyper.lltypesystem import rffi
from rpython.rlib import clibffi
from rpython.rlib.unroll import unrolling_iterable
from rpython.rlib.rbigint import rbigint

unrolling_types = unrolling_iterable([rffi.INT,
                                      rffi.DOUBLE,
                                      rffi.VOIDP])

class W_FunctionObject(W_PointerObject):
    classdef = ClassDef('Function', W_PointerObject.classdef)

    @classdef.singleton_method('allocate')
    def singleton_method_allocate(self, space, args_w):
        return W_FunctionObject(space)

    def __init__(self, space):
        W_PointerObject.__init__(self, space)
        self.w_ret_type = W_TypeObject(space, rffi.CHAR, clibffi.ffi_type_void)
        self.arg_types_w = []
        self.w_name = space.newsymbol('')
        self.ptr = None

    @classdef.method('initialize')
    def method_initialize(self, space, w_ret_type, w_arg_types,
                          w_name=None, w_options=None):
        if w_options is None: w_options = space.newhash()
        self.w_ret_type = self.ensure_w_type(space, w_ret_type)
        self.arg_types_w = [self.ensure_w_type(space, w_type)
                          for w_type in space.listview(w_arg_types)]
        self.w_name = self.dlsym_unwrap(space, w_name) if w_name else None

    @staticmethod
    def ensure_w_type(space, w_type_or_sym):
        w_type = None
        if space.is_kind_of(w_type_or_sym, space.getclassfor(W_TypeObject)):
            w_type = w_type_or_sym
        else:
            try:
                sym = Coerce.symbol(space, w_type_or_sym)
            except RubyError:
                tp = w_type_or_sym.getclass(space).name
                raise space.error(space.w_TypeError,
                                  "can't convert %s into Type" % tp)
            try:
                w_type_cls = space.getclassfor(W_TypeObject)
                w_type = space.find_const(w_type_cls, sym.upper())
            except RubyError:
                raise space.error(space.w_TypeError,
                                  "can't convert Symbol into Type")
        assert isinstance(w_type, W_TypeObject)
        return w_type

    @staticmethod
    def dlsym_unwrap(space, w_name):
        try:
            return space.send(w_name, 'to_sym')
        except RubyError:
            raise space.error(space.w_TypeError,
                            "can't convert %s into FFI::DynamicLibrary::Symbol"
                              % w_name.getclass(space).name)

    @classdef.method('call')
    def method_call(self, space, args_w):
        # NOT RPYTHON
        w_ret_type = self.w_ret_type
        arg_types_w = self.arg_types_w
        native_arg_types = [t.native_type for t in arg_types_w]
        native_ret_type = w_ret_type.native_type
        args = [space.float_w(w_x) for w_x in args_w]
        for i, argval in enumerate(args):
            argtype = native_arg_types[i]
            for t in unrolling_types:
                if t is argtype:
                    #casted_val = rffi.cast(t, argval)
                    #self.ptr.push_arg(casted_val)
                    print argtype
        for t in unrolling_types:
            if t is native_ret_type:
                if t is not rffi.VOIDP:
                    #result = self.ptr.call(t)
                    #result = rffi.cast(t, result)
                    #if t is rffi.INT:
                    #    bigres = rbigint.fromrarith_int(result)
                    #    return space.newbigint_fromrbigint(bigres)
                    #elif t is rffi.DOUBLE:
                    #    return space.newfloat(result)
                    return space.newfloat(1.0)
                else:
                    return space.w_nil
        assert 0
        return space.w_nil

    @classdef.method('attach', name='str')
    def method_attach(self, space, w_lib, name):
        w_ret_type = self.w_ret_type
        arg_types_w = self.arg_types_w
        w_ffi_libs = space.find_instance_var(w_lib, '@ffi_libs')
        for w_dl in w_ffi_libs.listview(space):
            ffi_arg_types = [t.ffi_type for t in arg_types_w]
            ffi_ret_type = w_ret_type.ffi_type
            ptr_key = self.w_name
            assert space.is_kind_of(ptr_key, space.w_symbol)
            try:
                self.ptr = w_dl.getpointer(space.symbol_w(ptr_key),
                                           ffi_arg_types,
                                           ffi_ret_type)
                w_attachments = space.send(w_lib, 'attachments')
                space.send(w_attachments, '[]=', [space.newsymbol(name), self])
            except KeyError: pass
