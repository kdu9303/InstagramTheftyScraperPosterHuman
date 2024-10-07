import sys
import logging
import random
import traceback
from time import sleep
from datetime import datetime, timedelta
from rich.console import Console
from automate_auth import relogin
from comment_generator import LlmModelBuilder
from instagrapi.exceptions import (
    LoginRequired,
    FeedbackRequired,
    ChallengeRequired,
    ChallengeUnknownStep,
)
from automate_notification import LogLevel, AlertType, send_slack_message


console = Console()

LLM_COMMENT_GENERATOR = LlmModelBuilder(model="gpt-4o-mini", temperature=0.9)

# 오류 누적 횟수
CONSECUTIVE_ERRORS = 0

# 한번 방문한 유저 기록
VISITED_CACHE = {}

# 미디어 Cache
MEDIA_LIST = []
MEDIA_COUNT = 0
MAX_MEDIA_USES = 15

# 전역 변수로 rate limit 카운터와 마지막 리셋 시간 추가
LIKE_COUNT = 0
COMMENT_COUNT = 0
FOLLOW_COUNT = 0
HOURLY_FOLLOW_COUNT = 0
LAST_RESET = datetime.now()
LAST_HOURLY_RESET = datetime.now()

# 새로운 상수 추가
MIN_ACTION_DELAY = 5 * 60
MAX_ACTION_DELAY = 20 * 60
DAILY_ACTION_LIMIT = 120  # 일일 총 액션 제한
SESSION_ACTION_LIMIT = 50  # 세션당 액션 제한
SESSION_DURATION = 4 * 60 * 60  # 세션 유지시간

# 새로운 전역 변수
TOTAL_DAILY_ACTIONS = 0
SESSION_ACTIONS = 0
SESSION_START_TIME = datetime.now()


def random_delay():
    return random.uniform(MIN_ACTION_DELAY, MAX_ACTION_DELAY)


def is_user_following(client, username) -> bool:
    result = client.search_following(client.user_id, username)
    return len(result) > 0


def is_user_follower(client, username) -> bool:
    result = client.search_followers(client.user_id, username)
    return len(result) > 0


def is_following_each_other(client, username) -> bool:
    is_following = is_user_following(client, username)
    sleep_time = random.uniform(10, 30)
    sleep(sleep_time)
    is_follower = is_user_follower(client, username)
    return is_following and is_follower


def get_new_media_list(client, tags):
    """Get a new list of media from a random tag."""
    random_tag = random.choice(tags)
    console.print(
        f"[bold yellow]Fetching new media for tag: {random_tag}[/bold yellow]"
    )

    actions = [
        lambda tag: client.hashtag_medias_recent_v1(tag, amount=50),
        lambda tag: client.hashtag_medias_top_v1(tag, amount=50),
        lambda tag: client.hashtag_medias_top(tag, amount=50),
    ]

    action = random.choice(actions)
    return action(random_tag)


def perform_comment_action(client, media_id, prompt_string, comment_count):
    """댓글 로직"""
    if comment_count < 200:
        comment_generated = LLM_COMMENT_GENERATOR.process_llm(prompt_string)
        comment_text = comment_generated.content
        client.media_comment(media_id, comment_text)
        console.print(
            f"[bold pink]Commented on media: {media_id} with text: \n{comment_text}.[/bold pink]"
        )
        return comment_count + 1
    else:
        console.print(
            "[bold yellow]Daily comment limit reached. Skipping comment.[/bold yellow]"
        )
        return comment_count


def perform_like_action(client, media_id, like_count):
    """좋아요 로직"""
    if like_count < 1000:
        client.media_like(media_id)
        console.print(f"[bold yellow]Liked media: {media_id}.[/bold yellow]")
        return like_count + 1
    else:
        console.print(
            "[bold yellow]Daily like limit reached. Skipping like.[/bold yellow]"
        )
        return like_count


def perform_follow_action(client, user_pk, follow_count, hourly_follow_count):
    """팔로잉 로직"""
    if follow_count < 200 and hourly_follow_count < 10:
        client.user_follow(user_pk)
        console.print(f"[bold white]Followed user: {user_pk}.[/bold white]")
        return follow_count + 1, hourly_follow_count + 1
    else:
        if follow_count >= 200:
            console.print(
                "[bold yellow]Daily follow limit reached. Skipping follow.[/bold yellow]"
            )
        return follow_count, hourly_follow_count


def simulate_profile_view(client, username):
    try:
        user_info = client.user_info_by_username(username)
        console.print(
            f"[bold cyan]Viewed profile of user: {user_info.username}[/bold cyan]"
        )
        sleep(random.uniform(5, 20))  # 프로필 보는 시간 시뮬레이션
    except Exception as e:
        console.print(f"[bold red]Error viewing profile: {str(e)}[/bold red]")


def simulate_story_view(client, user_pk):
    try:
        stories = client.user_stories(user_pk)
        if stories:
            console.print(
                f"[bold cyan]Viewed story of user: {stories[0].user.username}[/bold cyan]"
            )
            sleep(random.uniform(2, 10))  # 스토리 보는 시간 시뮬레이션
    except Exception as e:
        console.print(f"[bold red]Error viewing story: {str(e)}[/bold red]")


def perform_human_actions(client, tags, login_username, login_password, session_file):
    global MEDIA_LIST, MEDIA_COUNT, CONSECUTIVE_ERRORS, LIKE_COUNT, COMMENT_COUNT, FOLLOW_COUNT, HOURLY_FOLLOW_COUNT, LAST_RESET, LAST_HOURLY_RESET, TOTAL_DAILY_ACTIONS, SESSION_ACTIONS, SESSION_START_TIME

    # 일일 및 세션 제한 확인
    if TOTAL_DAILY_ACTIONS >= DAILY_ACTION_LIMIT:
        console.print(
            "[bold red]Daily action limit reached. Ending session.[/bold red]"
        )
        return

    if (
        SESSION_ACTIONS >= SESSION_ACTION_LIMIT
        or (datetime.now() - SESSION_START_TIME).total_seconds() >= SESSION_DURATION
    ):
        console.print(
            "[bold yellow]Session limit reached. Taking a break.[/bold yellow]"
        )
        sleep(random.uniform(1 * 60 * 60, 3 * 60 * 60))  # 1-3시간 휴식
        SESSION_ACTIONS = 0
        SESSION_START_TIME = datetime.now()

    # 일일 리셋 확인
    now = datetime.now()
    if now - LAST_RESET > timedelta(days=1):
        LIKE_COUNT = 0
        COMMENT_COUNT = 0
        FOLLOW_COUNT = 0
        TOTAL_DAILY_ACTIONS = 0
        LAST_RESET = now

    # 시간당 팔로우 리셋 확인
    if now - LAST_HOURLY_RESET > timedelta(hours=1):
        HOURLY_FOLLOW_COUNT = 0
        LAST_HOURLY_RESET = now

    if not MEDIA_LIST or MEDIA_COUNT >= MAX_MEDIA_USES:
        MEDIA_LIST = get_new_media_list(client, tags)
        MEDIA_COUNT = 0

    if not MEDIA_LIST:
        console.print(
            "[bold bright_red]No media found for the current tag.[/bold bright_red]"
        )
        return

    try:
        # 미디어 선택 전 랜덤 지연
        sleep(random_delay())

        media = random.choice(MEDIA_LIST)
        MEDIA_COUNT += 1

        media_json = media.model_dump()
        media_id = media_json["pk"]
        media_content = media_json["caption_text"]

        comments = client.media_comments(media_id, amount=10)
        comments_chunk = [comment.model_dump()["text"] for comment in comments]
        comments_str = "\n".join(comments_chunk)

        user_pk = media_json["user"]["pk"]
        media_user_id = media_json["user"]["username"]
        user_description = media_json["user"]["full_name"]

        # 프로그램 실행중 유저 캐시 처리
        if user_pk in VISITED_CACHE:
            console.print(
                f"[bold cyan]Already visited user: {media_user_id}. Skipping....[/bold cyan]"
            )
            return
        VISITED_CACHE[user_pk] = media_user_id
        console.print(f"[bold green]New user visited: {media_user_id}[/bold green]")

        sleep(random.uniform(5,10))

        # 유저 팔로워 수가 많은 경우 처리
        user_follower_max = 5000
        user_follower_count = client.user_info_by_username(media_user_id).model_dump()[
            "follower_count"
        ]
        if user_follower_count > user_follower_max:
            console.print(
                f"[bold green]유저의 팔로워 수 조건 초과로 다음 게시물로 넘어갑니다[/bold green]"
            )
            return

        sleep(random_delay())

        is_follower_following = is_following_each_other(client, media_user_id)
        if is_follower_following:
            console.print(f"현재 user {media_user_id}와 맞팔 중입니다")
            return

        prompt_parts = [
            f"Media user id: {media_user_id}",
            f"Media user description: {user_description}",
            "[게시글 내용]",
            f"Media contents: {media_content}",
            "[댓글 내용]",
            f"Media comments: {comments_str}",
        ]

        prompt_string = "\n\n".join(prompt_parts)
        console.print(f"[bold cyan]{prompt_string}[/bold cyan]")

        sleep(random_delay())

        # 댓글, 좋아요, 팔로우 액션 전 추가 검사
        if random.random() < 0.4:  # 40% 확률로 프로필 보기
            simulate_profile_view(client, media_user_id)
            TOTAL_DAILY_ACTIONS += 1
            SESSION_ACTIONS += 1

        if random.random() < 0.3:  # 30% 확률로 스토리 보기
            simulate_story_view(client, user_pk)
            TOTAL_DAILY_ACTIONS += 1
            SESSION_ACTIONS += 1

        # 댓글 로직
        COMMENT_COUNT = perform_comment_action(
            client, media_id, prompt_string, COMMENT_COUNT
        )
        TOTAL_DAILY_ACTIONS += 1
        SESSION_ACTIONS += 1
        sleep(random_delay())

        # 좋아요 로직
        LIKE_COUNT = perform_like_action(client, media_id, LIKE_COUNT)
        TOTAL_DAILY_ACTIONS += 1
        SESSION_ACTIONS += 1
        sleep(random_delay())

        # 팔로우 로직
        FOLLOW_COUNT, HOURLY_FOLLOW_COUNT = perform_follow_action(
            client, user_pk, FOLLOW_COUNT, HOURLY_FOLLOW_COUNT
        )
        TOTAL_DAILY_ACTIONS += 1
        SESSION_ACTIONS += 1

        # 액션 후 랜덤 지연
        sleep_time = random.uniform(5 * 60, 15 * 60)  # 5-15분
        console.print(
            f"[bold yellow]Sleeping for {sleep_time:.2f} seconds to mimic human behavior.[/bold yellow]"
        )
        sleep(sleep_time)

        # 연속 오류 횟수 초기화
        CONSECUTIVE_ERRORS = 0

    except LoginRequired:
        try:
            relogin(client, login_username, login_password, session_file)
        except Exception:
            send_slack_message(level=LogLevel.ERROR, alert=AlertType.LOGIN_REQUIRED)
    except FeedbackRequired:
        console.print(
            f"[bold red]댓글 작성 금지 게시물입니다. 다음 게시글로 넘어갑니다[/bold red]"
        )
        return
    except ChallengeUnknownStep:
        try:
            console.print(
                f"[bold red]커뮤니티 가이드 위반 사항에 대한 조치가 있었습니다. 확인 요망[/bold red]"
            )
        finally:
            send_slack_message(
                level=LogLevel.WARNING,
                alert=AlertType.CHALLENGE_UNKNOWN_STEP,
            )

    except ChallengeRequired:
        try:
            console.print(
                f"[bold red]자동화 프로그램 의심으로 유저 개입이 필요합니다.\n앱에서 직접 인증절차를 진행해주세요[/bold red]"
            )
            logging.error(f"Unexpected error: {traceback.format_exc()}")
        finally:
            send_slack_message(
                level=LogLevel.CRITICAL,
                alert=AlertType.CHALLENGE_REQUIRED,
            )
            # 챌린지 해결 대기시간
            sleep(10 * 60)
            console.print(
                "[bold red]챌린지 인증과정 해결까지 일시 대기합니다...[/bold red]"
            )
            try:
                console.print("[bold green]로그인 정보 갱신을 시도합니다[/bold green]")
                relogin(client, login_username, login_password, session_file)
                return
            except ChallengeRequired:
                sys.exit(1)

    except Exception:
        CONSECUTIVE_ERRORS += 1
        console.print(
            f"[bold red]Failed to perform human-like actions: \n{traceback.format_exc()}.[/bold red]"
        )
        logging.error(
            f"Failed to perform human-like actions: \n{traceback.format_exc()}"
        )
        if CONSECUTIVE_ERRORS == 3:
            send_slack_message(
                level=LogLevel.ERROR,
                alert=AlertType.UNKNOWN,
                message=traceback.format_exc(),
            )

        error_max_count = 6
        if CONSECUTIVE_ERRORS >= error_max_count:
            console.print(
                f"[bold red]연속 오류가 {error_max_count}회 발생했습니다. 프로그램을 종료합니다.[/bold red]"
            )
            send_slack_message(
                level=LogLevel.CRITICAL,
                alert=AlertType.UNKNOWN,
                message=f"연속 오류가 {error_max_count}회 발생했습니다. 프로그램을 종료합니다",
            )
            sys.exit(1)
