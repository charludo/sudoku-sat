ks = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def and_clause(ks):
    return " & ".join(ks)


def or_clause(ks):
    return " | ".join(ks)


def grouped(clause):
    return f"({clause})" if len(clause) else None
