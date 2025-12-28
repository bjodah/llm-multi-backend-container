from . import case_classes
from .refactored_readme import client, Config

if __name__ == '__main__':
    import argh

    max_tok_per_model = {}
    models = client.models.list()
    for entry in models.data:
        if not any(fragment in entry.id.lower() for fragment in ['devstral-2', 'devstral-small-2']):
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
            case_(cfg)

    argh.dispatch_command(all_cases)
