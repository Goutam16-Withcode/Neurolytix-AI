try:
    from src import llm_engine
    print('LLM engine imports successfully')
except Exception as e:
    print(f'Import failed: {e}')
    import traceback
    traceback.print_exc()