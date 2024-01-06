from __future__ import annotations
from enum import Enum


class SymbolCategory(Enum):
    Var = "Var"
    Argument = "Argument"
    Static = "Static"
    Field = "Field"
    Class = "Class"
    Subroutine = "Subroutine"


category_to_segment = {
    SymbolCategory.Static: "static",
    SymbolCategory.Field: "this",
    SymbolCategory.Argument: "argument",
    SymbolCategory.Var: "local",
}


class SymbolTable:
    _symbols: dict[str, dict] = None
    fallback: SymbolTable | None

    def __init__(self, fallback: SymbolTable | None = None):
        self._symbols = {}
        self.fallback = fallback

    def add_symbol(self, name: str, type: str, category: SymbolCategory):
        categorySymbols = self._symbols.get(category)
        if categorySymbols is None:
            categorySymbols = self._symbols[category] = {}
        elif categorySymbols.get(name):
            return
        categorySymbols[name] = {
            "index": len(categorySymbols),
            "type": type,
            "category": category,  # Looks reudandant but helps optimizing symbol retrieval
            "memory_segment": category_to_segment[category],
        }

    def get_by_name(self, name: str):
        for symbols in self._symbols.values():
            if name in symbols:
                return symbols[name]
        if self.fallback:
            return self.fallback.get_by_name(name)
        return None

    def category_symbols(self, category: SymbolCategory):
        return self._symbols.get(category, {})

    def count_by_category(self, category: SymbolCategory):
        return len(self.category_symbols(category))
