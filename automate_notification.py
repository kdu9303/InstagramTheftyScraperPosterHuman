import os
import pytz
import requests
from dotenv import load_dotenv
from enum import Enum
from typing import Dict, Any
from datetime import datetime


load_dotenv()


class LogLevel(Enum):
    CRITICAL = {"level": "Critical", "message": "빠른 조치 필요"}
    ERROR = {"level": "Error", "message": "디버깅 필요"}
    WARNING = {"level": "Warning", "message": "주의 필요"}
    INFO = {"level": "Info", "message": "알림"}


class AlertType(Enum):
    """CRITICAL OR ERROR 발생시"""

    CHALLENGE_REQUIRED = "자동화 프로그램 의심으로 유저 개입이 필요합니다.\n앱에서 직접 인증절차를 진행해주세요"
    LOGIN_REQUIRED = "재로그인에 실패하였습니다.\n로그인 절차가 필요합니다."
    FEEDBACKREQUIRED = "댓글 작성 금지 게시물에 접근하였습니다."
    CHALLENGE_UNKNOWN_STEP = "커뮤니티 가이드 위반 사항에 대한 조치가 있었습니다. 확인 요망"
    UNKNOWN = "원인 불명의 오류가 발생하였습니다."
    CONFIRMED = "조치 불필요"
    DAILY_LIMIT_REACHED = "일별 요청 수 제한에 도달했습니다."


def slack_notification_content(
    level: LogLevel, alert: AlertType = None, **kwargs
) -> Dict[str, Any]:
    """
    사용 예시:
    slack_data = slack_notification_content(
        level=LogLevel.CRITICAL,
        alert=AlertType.CHALLENGE_REQUIRED,
    )
    """
    # 한국 시간대 설정
    korea_tz = pytz.timezone("Asia/Seoul")
    current_time = datetime.now(korea_tz)

    # 시간 포맷팅
    formatted_time = current_time.strftime("%Y년 %m월 %d일 %p %I시 %M분")
    formatted_time = formatted_time.replace("AM", "오전").replace("PM", "오후")

    # kwargs 정의
    follower_count = kwargs.get("follower_count")
    difference = kwargs.get("difference")
    message = kwargs.get("message")

    if level == LogLevel.INFO:

        slack_data = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "[알림] 팔로워 정보 변동 안내",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*알림시각:* {formatted_time}",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*현재 팔로워 수:*\n{follower_count}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*팔로워 증감 수:*\n`{difference}`",
                        },
                    ],
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{message}",
                    },
                },
                {"type": "divider"},
            ]
        }

    else:
        slack_data = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"[오류 알림] {alert.name} - {level.value.get('message')}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*발생시각:* {formatted_time}",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Level:*\n`{level.value.get('level')}`",
                        },
                        {"type": "mrkdwn", "text": f"*Alert Name:*\n`{alert.name}`"},
                    ],
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{message if message else alert.value}",
                    },
                },
                {"type": "divider"},
            ]
        }
    return slack_data


def send_slack_message(level, alert, **kwargs):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL_TEST")
    headers = {"Content-type": "application/json"}

    slack_data = slack_notification_content(level=level, alert=alert, **kwargs)

    response = requests.post(webhook_url, headers=headers, json=slack_data)

    if response.text != "ok":
        raise Exception("Could not send slack message")


def main():
    error_level = LogLevel.CRITICAL
    alert_type = AlertType.UNKNOWN

    # kwargs로 전달할 값 정의
    follower_count = 1500  # 예시 값
    difference = 50  # 예시 값
    message = "유저 활동이 증가하고 있습니다."  # 예시 메시지

    send_slack_message(
        level=error_level,
        alert=alert_type,
        follower_count=follower_count,
        difference=difference,
        message=message,
    )


if __name__ == "__main__":
    main()
