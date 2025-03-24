import logging
# 로그 파일 생성
# 시스템 실행 중에 발생하는 이벤트를 시간의 순서대로 기록한 파일
# 버그. 문제, 활동 모니터링... 용도로 사용
# 로고 레벨(error, warning, info, debug)
def make_logger(fileNm, name="custom_logger"):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # level 설정
        logger.setLevel(logging.DEBUG)
        format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # 콘솔
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(format)
        # 파일
        file_handler = logging.FileHandler(filename=fileNm, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(format)
        logger.addHandler(console)
        logger.addHandler(file_handler)
    return logger
if __name__ == '__main__':
    logger = make_logger("app.log", "text")
    logger.debug("디버그 메세지 입니다.")
    logger.info("정보 메세지 입니다.")
    logger.warning("경고 메세지")
    logger.error("심각한 오류")
    logger.critical("진짜 위험한 오류!!")