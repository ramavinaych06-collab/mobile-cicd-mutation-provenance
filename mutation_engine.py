"""
mutation_engine.py
AST-based Mutation Testing Engine for Mobile CI/CD pipelines.
Applies Relational (ROR) and Arithmetic (AOR) operator replacements.
"""

import ast


class ASTMutationEngine(ast.NodeTransformer):
    def __init__(self, target_idx: int = -1):
        super().__init__()
        self.target_idx = target_idx
        self.mutations_found = 0
        self.mutation_desc = ""

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        replacements = {
            ast.Lt: ast.GtE,
            ast.Gt: ast.LtE,
            ast.LtE: ast.Gt,
            ast.GtE: ast.Lt,
            ast.Eq: ast.NotEq,
            ast.NotEq: ast.Eq,
        }
        new_ops = []
        for op in node.ops:
            op_cls = type(op)
            if op_cls in replacements:
                if self.mutations_found == self.target_idx:
                    new_op = replacements[op_cls]()
                    new_ops.append(new_op)
                    self.mutation_desc = (
                        f"ROR: {op_cls.__name__} -> {type(new_op).__name__} (Line {node.lineno})"
                    )
                else:
                    new_ops.append(op)
                self.mutations_found += 1
            else:
                new_ops.append(op)
        node.ops = new_ops
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        replacements = {
            ast.Add: ast.Sub,
            ast.Sub: ast.Add,
            ast.Mult: ast.FloorDiv,
        }
        op_cls = type(node.op)
        if op_cls in replacements:
            if self.mutations_found == self.target_idx:
                new_op = replacements[op_cls]()
                node.op = new_op
                self.mutation_desc = (
                    f"AOR: {op_cls.__name__} -> {type(new_op).__name__} (Line {node.lineno})"
                )
            self.mutations_found += 1
        return node