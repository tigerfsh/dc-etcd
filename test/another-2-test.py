from tenacity import retry, stop_after_attempt, wait_func  
import time  
  
def my_custom_wait(retry_state):  
    # 假设我们想在第一次重试后等待1秒，之后每次重试等待时间翻倍  
    if retry_state.attempt_number == 1:  
        return 1  
    else:  
        return 2 ** (retry_state.attempt_number - 2)  
  
@retry(wait=wait_func(my_custom_wait), stop=stop_after_attempt(3))  
def test_function():  
    print(f"Attempt {test_function.retry.statistics.attempt_number}")  
    print("Function is being retried...")  
    raise Exception("Something went wrong!")  
  
test_function()
