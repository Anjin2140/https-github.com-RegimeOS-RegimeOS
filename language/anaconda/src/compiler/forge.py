# forge.py
# Project ANACONDA Compiler Frontend v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import os
import ast
import copy
import sys
import argparse

class StrictLumberVisitor(ast.NodeVisitor):
    """
    Read-Only AST Parser. Strictly analyzes code structure without executing any code.
    Rejects eval, exec, and importlib under --strict-lumber flag.
    """
    def __init__(self):
        self.prohibited_funcs = {"eval", "exec"}
        self.prohibited_imports = {"importlib", "socket", "urllib", "requests", "http", "aiohttp", "pika"}

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.prohibited_funcs:
                raise PermissionError(f"Security Violation: Prohibited function call '{node.func.id}' detected.")
        self.generic_visit(node)

    def visit_Import(self, node):
        for name in node.names:
            base_module = name.name.split('.')[0]
            if base_module in self.prohibited_imports:
                raise PermissionError(f"Security Violation: Prohibited import '{name.name}' detected.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in self.prohibited_imports:
                raise PermissionError(f"Security Violation: Prohibited import from '{node.module}' detected.")
        self.generic_visit(node)


class AnacondaASTTransformer(ast.NodeTransformer):
    """
    AST rewriter operating on cloned AST nodes to transpile standard Python types to ANACONDA types.
    """
    def __init__(self, filename="<string>"):
        super().__init__()
        self.filename = filename

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, (float, bool)) or node.value.value is None:
                target_names = []
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        target_names.append(target.id)
                var_name = ", ".join(target_names) if target_names else "unknown"
                line = getattr(node, "lineno", "?")
                val_str = str(node.value.value)
                print(f"[COMPILE_TIME_WARNING] Implicit promotion of '{val_str}' to ANACONDA type for variable '{var_name}' at {self.filename}:{line}")
        self.generic_visit(node)
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, float):
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='RegimeDecimal', ctx=ast.Load()),
                    attr='from_str',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=str(node.value))],
                keywords=[]
            )
        elif isinstance(node.value, bool):
            val = 1 if node.value else -1
            return ast.Call(
                func=ast.Name(id='Ternary', ctx=ast.Load()),
                args=[ast.Constant(value=val)],
                keywords=[]
            )
        elif node.value is None:
            return ast.Call(
                func=ast.Name(id='Ternary', ctx=ast.Load()),
                args=[ast.Constant(value=0)],
                keywords=[]
            )
        return self.generic_visit(node)

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load):
            return self.generic_visit(node)
        if node.id == "TRUE":
            return ast.Call(
                func=ast.Name(id='Ternary', ctx=ast.Load()),
                args=[ast.Constant(value=1)],
                keywords=[]
            )
        elif node.id == "FALSE":
            return ast.Call(
                func=ast.Name(id='Ternary', ctx=ast.Load()),
                args=[ast.Constant(value=-1)],
                keywords=[]
            )
        elif node.id in ("UNKNOWN", "PARADOX"):
            return ast.Call(
                func=ast.Name(id='Ternary', ctx=ast.Load()),
                args=[ast.Constant(value=0)],
                keywords=[]
            )
        elif node.id in ("epsilon", "eps"):
            return ast.Call(
                func=ast.Name(id='HahnDecimal', ctx=ast.Load()),
                args=[
                    ast.Attribute(
                        value=ast.Name(id='RegimeDecimal', ctx=ast.Load()),
                        attr='One',
                        ctx=ast.Load()
                    ),
                    ast.Constant(value=1)
                ],
                keywords=[]
            )
        return self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == "float":
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='RegimeDecimal', ctx=ast.Load()),
                        attr='from_float',
                        ctx=ast.Load()
                    ),
                    args=node.args,
                    keywords=node.keywords
                )
            elif node.func.id == "bool":
                return ast.Call(
                    func=ast.Name(id='Ternary', ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords
                )
        return self.generic_visit(node)


def transpile_code(source_code: str, strict_lumber: bool = False, filename: str = "<string>") -> str:
    """
    Parses, validates, and transforms legacy Python code into ANACONDA-IR Python.
    """
    original_tree = ast.parse(source_code)

    if strict_lumber:
        visitor = StrictLumberVisitor()
        visitor.visit(original_tree)

    cloned_tree = copy.deepcopy(original_tree)

    is_kernel = os.path.basename(filename) in ("regime_math.ana", "regime_math.py")
    if not is_kernel:
        transformer = AnacondaASTTransformer(filename)
        transformed_tree = transformer.visit(cloned_tree)
    else:
        transformed_tree = cloned_tree
        
    ast.fix_missing_locations(transformed_tree)

    transpiled_body = ast.unparse(transformed_tree)

    is_kernel = os.path.basename(filename) in ("regime_math.ana", "regime_math.py")
    
    # Prepend capabilities declarations to the output header
    capabilities_header = ""
    for line in source_code.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("# @capability:"):
            capabilities_header += line_strip + "\n"
        elif line_strip and not line_strip.startswith("#"):
            # Stop at the first non-comment line
            break

    header = (
        capabilities_header +
        "# Transpiled by ANACONDA Forge v1.0\n"
        "import sys\n"
        "if r'C:\\RegimeOS\\language\\anaconda' not in sys.path:\n"
        "    sys.path.insert(0, r'C:\\RegimeOS\\language\\anaconda')\n"
    )
    if not is_kernel:
        header += "from src.kernel.regime_math import Ternary, RegimeDecimal, HahnDecimal\n\n"
    else:
        header += "\n"
        
    header += (
        "# Verify execution authorization\n"
        "if __name__ == \"__anaconda_secure__\":\n"
        "    try:\n"
        "        from src.compiler.vault import verify_air_signature\n"
        "        if not verify_air_signature(__file__):\n"
        "            print(\"EXIT_CODE_SECURITY_VIOLATION\")\n"
        "            sys.exit(99)\n"
        "    except Exception:\n"
        "        print(\"EXIT_CODE_SECURITY_VIOLATION\")\n"
        "        sys.exit(99)\n\n"
    )

    return header + transpiled_body


def main():
    parser = argparse.ArgumentParser(description="ANACONDA Forge Transpiler Frontend")
    parser.add_argument("--ingest", type=str, required=True, help="Path to Python script to ingest ('The Lumber')")
    parser.add_argument("--output", type=str, required=True, help="Destination path for the compiled output")
    parser.add_argument("--strict-lumber", action="store_true", help="Reject scripts containing eval(), exec() or importlib")

    args = parser.parse_args()

    if not os.path.exists(args.ingest):
        print(f"[!] Input file does not exist: {args.ingest}")
        sys.exit(1)

    try:
        with open(args.ingest, "r", encoding="utf-8") as f:
            source = f.read()

        transpiled = transpile_code(source, strict_lumber=args.strict_lumber, filename=args.ingest)

        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(transpiled)

        print(f"[+] Successfully transpiled '{args.ingest}' -> '{args.output}'")
        
        # Sign the transpiled code file
        try:
            from src.compiler import vault
            vault.sign_air_file(args.output)
        except ImportError:
            sys.path.insert(0, r"C:\RegimeOS\language\anaconda")
            from src.compiler import vault
            vault.sign_air_file(args.output)

        # Regenerate manifest since compiler source has modified/created output files
        vault.generate_manifest()

    except Exception as e:
        print(f"[!] Compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
