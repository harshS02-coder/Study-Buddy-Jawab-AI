from concurrent.futures import ThreadPoolExecutor

# Single executor for the entire app
executor = ThreadPoolExecutor(max_workers=2)