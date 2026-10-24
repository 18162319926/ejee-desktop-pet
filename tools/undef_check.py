# -*- coding: utf-8 -*-
"""迷你 pyflakes v3：AST 收集「用了但没定义」的全局名。

用途：拆文件/搬代码时漏 import 的静态防线。这类 bug 的经典形态是
`ejee_ui.py` 的 `BreadCursor._poll` 用了 `QCursor` 却没导入——定时器
每 16ms 抛一次 NameError，源码跑有 traceback、打包成无控制台 exe 后
完全静默，功能直接冻住（2026-10-23 实测案例）。

v3 修正 v2 的自身 bug：赋值收集只收 targets（Store），不再把
`gp = QCursor.pos()` 右侧的 Load 名误当本地变量。

用法：python undef_check.py <file.py> [more.py ...]
"""
import ast
import builtins
import sys


def check(path):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src, path)
    defined = set(dir(builtins))
    used = {}

    class V(ast.NodeVisitor):
        def __init__(self):
            self.scopes = [set()]

        def cur(self):
            return self.scopes[-1]

        def _bind_target(self, target):
            """只收 Store 语义的绑定目标（赋值左侧/for 目标等）。"""
            if isinstance(target, ast.Name):
                self.cur().add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    self._bind_target(elt)
            elif isinstance(target, ast.Starred):
                self._bind_target(target.value)

        def visit_Import(self, n):
            for a in n.names:
                defined.add((a.asname or a.name).split(".")[0])

        def visit_ImportFrom(self, n):
            for a in n.names:
                defined.add(a.asname or a.name)

        def _def(self, n):
            defined.add(n.name)
            self.scopes.append(set())
            args = n.args
            for a in (getattr(args, "posonlyargs", []) + args.args
                      + args.kwonlyargs):
                self.cur().add(a.arg)
            if args.vararg:
                self.cur().add(args.vararg.arg)
            if args.kwarg:
                self.cur().add(args.kwarg.arg)
            for d in n.decorator_list:
                self.visit(d)
            for d in list(args.defaults) + [x for x in args.kw_defaults
                                            if x]:
                self.visit(d)
            self.generic_visit(n)
            self.scopes.pop()

        visit_FunctionDef = _def
        visit_AsyncFunctionDef = _def

        def visit_Lambda(self, n):
            self.scopes.append(set())
            args = n.args
            for a in args.args + args.kwonlyargs:
                self.cur().add(a.arg)
            if args.vararg:
                self.cur().add(args.vararg.arg)
            if args.kwarg:
                self.cur().add(args.kwarg.arg)
            self.generic_visit(n)
            self.scopes.pop()

        def visit_ClassDef(self, n):
            defined.add(n.name)
            self.scopes.append(set())
            self.generic_visit(n)
            self.scopes.pop()

        def visit_Assign(self, n):
            for t in n.targets:
                self._bind_target(t)
            self.visit(n.value)

        def visit_AnnAssign(self, n):
            self._bind_target(n.target)
            if n.annotation:
                self.visit(n.annotation)
            if n.value:
                self.visit(n.value)

        def visit_AugAssign(self, n):
            self._bind_target(n.target)
            self.visit(n.value)

        def visit_For(self, n):
            self._bind_target(n.target)
            self.generic_visit(n)

        visit_AsyncFor = visit_For

        def _comp(self, n):
            self.scopes.append(set())
            for gen in n.generators:
                self._bind_target(gen.target)
                for cond in gen.ifs:
                    self.visit(cond)
                self.visit(gen.iter)
            if isinstance(n, ast.DictComp):
                self.visit(n.key)
                self.visit(n.value)
            else:
                self.visit(n.elt)
            self.scopes.pop()

        visit_ListComp = _comp
        visit_SetComp = _comp
        visit_DictComp = _comp
        visit_GeneratorExp = _comp

        def visit_With(self, n):
            for item in n.items:
                if item.optional_vars:
                    self._bind_target(item.optional_vars)
            self.generic_visit(n)

        visit_AsyncWith = visit_With

        def visit_ExceptHandler(self, n):
            if n.name:
                self.cur().add(n.name)
            self.generic_visit(n)

        def visit_Global(self, n):
            for nm in n.names:
                defined.add(nm)

        def visit_NamedExpr(self, n):
            self._bind_target(n.target)
            self.visit(n.value)

        def visit_Name(self, n):
            if isinstance(n.ctx, ast.Load):
                if n.id.startswith("__") and n.id.endswith("__"):
                    return          # __file__ 等运行时注入的 dunder，不查
                if n.id not in defined and not any(
                        n.id in s for s in self.scopes):
                    used.setdefault(n.id, n.lineno)

    V().visit(tree)
    bad = False
    for name, line in sorted(used.items(), key=lambda kv: kv[1]):
        print("%s:%d: undefined name %r" % (path, line, name))
        bad = True
    if not bad:
        print("%s: OK" % path)


for p in sys.argv[1:]:
    check(p)
