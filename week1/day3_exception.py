print("시작")
try:
    print("^^^"%4)
except Exception as e:
    print(str(e))
print("종료")

def calc(values):
    sum = 0
    try:
        sum = values[0] + values[1] + values[2]
    except IndexError as e:
        print("인덱스 에러!!")
    except Exception as e:
        print("여러 오류도!")
    else:
        print("정상 처리 일 떄만")
    finally:
        print("무조건 처리되는")
calc([1, 2, 3]) # else, finally
calc([1, 2])    # index, finally
calc([None]) # exception, finally