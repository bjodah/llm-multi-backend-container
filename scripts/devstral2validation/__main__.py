import re
from . import case_classes
from .refactored_readme import client, Config

fragments = [re.compile(_) for _ in (r'\b[Dd]evstral-2\b', r'\b[Dd]evstral-[Ss]mall-2\b')]

if __name__ == '__main__':
    import argh

    max_tok_per_model = {}
    models = client.models.list()
    for entry in models.data:
        if not any(frag.search(entry.id) for frag in fragments):
            continue
        try:
            max_tok_per_model[entry.id] = entry.meta['llamaswap']['context_window']
        except (KeyError, AttributeError):
            max_tok_per_model[entry.id] = None

    print(f"{max_tok_per_model=}")  # diagnostic / debug-print

    def all_cases(model):
        cfg = Config(model=model, max_tokens=max_tok_per_model[model])
        five_cases = [Case(cfg) for Case in case_classes]

        for case_ in five_cases:
            case_()

    argh.dispatch_command(all_cases)
