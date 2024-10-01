import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from templates.prmpt_template import instagram_template, test_template

load_dotenv()
# os.environ["LANGCHAIN_TRACING_V2"] = "true"

class LlmModelBuilder:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.5,
    ):

        self.model = model
        self.temperature = temperature
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def set_templetes(self, message: str):
        prompt = PromptTemplate.from_template(instagram_template)
        return prompt.format(input=message)

    def create_model(self):
        llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model_name=self.model,
            temperature=self.temperature,
        )
        return llm

    def process_llm(self, message: str):
        prompt = self.set_templetes(message)
        llm = self.create_model()
        result = llm.invoke(prompt)
        return result


if __name__ == "__main__":
    message = """
    [게시글 내용]
    Media contents 오늘도 6시간 동안 가동한
    #yummysmell반찬가게 🍱
    .
    하루 사이에 날씨가 선선해져서
    이제 음식 할 맛 난다 나!!!💪💪
    .
    명절에 못 먹었던 잡채도 만들고
    요즘 금값이라는 시금치도 무치고..😋😋😋
    .
    반찬 많아서 든든함 그 잡채!!😍😍😍
    .
    무생채, 크래미깻잎전, 부추양파무침, 두부조림,
    소세지야채볶음, 시금치무침, 계란말이, 잡채,
    사라다, 진미채볶음, 가지볶음, 무말랭이무침,
    고추멸치볶음, 콩나물무침, 오이무침, 감자야채볶음
    .
    .
    #집밥#요리#쿡스타그램#요리스타그램#홈쿡#맛스타그램#홈메이드#대존맛#koreanfood#존맛#먹스타#가을#냠냠#먹스타그램#두부조림#반찬
    스타그램#나물반찬#잡채#감자볶음#나물반찬#주말#계란말이#반찬#한식#주말메뉴#밥도둑#밑반찬#반찬공장#반찬데이#rice.

    [댓글 내용]
    Media comments @lovelybbo__ 앜ㅋㅋㅋㅋ😍😍😍 예쁜 미스코리아 보경님이드아아아아❤️❤️❤️❤️
    @lovelykno002 요거 간단해용!😆 저는 올리브유 두른 팬 가열되면 고추만 넣고 중간불에서 볶다가 샛파랏게 색이 변했을때쯤 간장,
    올리고당 조금, 멸치, 져민 양파 넣고 볶다가 마지막에 다진 마늘, 채썬 파 넣고 살짝 더 볶다가 불꺼요!! 참기름 한 수저 두르고,
    깨소금 슉슉 뿌리면 완성입니다.😋
    @yoon.y.jang 으아아악😍 감쏴함돠아아아아!!!🤩👍❤️👍
    정말 최고옹🤍🤍🤍🤍
    😍고추멸치볶음 레시피가 궁금해용~~^^
    👏👏👏👏 예술이네여 👏👏👏👏
    @myunghee_homecook 평일에 내가 거의 음식해서 명절은 엄마 찬스라 명절에 난 한게 없;;;;😝😝😝😝 일요일까지 푸욱 쉬어🔥
    알코올은 당분간 머얼리 하고..ㅋㅋㅋㅋㅋㅋㅋㅋㅋ
    명절 지난지 얼마 안되었는데도 이런 반찬가게.. 아니 반찬 데이라니 !! ㅎㅎㅎㅎ 나는 일요일까지는 좀 쉬고 월요일부터 열 일
    하려고 ㅋ
    @call.you_mine 반찬 많으니 내일부터 메인메뉴 한개만 만들면 되서 너어어무 편해요.😍😍😍
    징짜 대단하셔용❤️❤️❤️
    밥한공기로는 안되겟어요 ㅎ
    두공기 순삭각😍😂😂.
    """

    builder = LlmModelBuilder(model="gpt-4o-mini", temperature=0.9)
    result = builder.process_llm(message)

    print(result.content)
