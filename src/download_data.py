"""
공공데이터포털 「국민연금공단_국민연금 가입 사업장 내역」 월별 CSV 다운로드 스크립트
https://www.data.go.kr/data/15083277/fileData.do  (로그인 없이 내려받을 수 있는 파일데이터)

사용법 (프로젝트 루트에서):  python src/download_data.py
- 각 파일은 약 110MB, 7개월분 합계 약 800MB
- 포털이 다운로드 횟수 제한으로 보안문자(CAPTCHA)를 요구하면 자동으로 멈춘다.
  그때는 위 페이지의 '과거 데이터' 목록에서 직접 내려받아 data/raw/ 에 아래 이름으로 저장하면 된다.
"""
import os
import requests

# 자료생성년월 : (포털 등록 파일명 날짜, 첨부파일 ID)
FILES = {
    '202512': ('20260123', 'FILE_000000003590996'),   # 12-1 시간 기반 검증용
    '202601': ('20260223', 'FILE_000000003602190'),   # 12-1 시간 기반 검증용
    '202603': ('20260423', 'FILE_000000003631347'),
    '202604': ('20260521', 'FILE_000000003644400'),
    '202606': ('20260723', 'FILE_000000003681205'),
    '202607': ('20260825', 'FILE_000000007629828'),
    '202610': ('20261123', 'FILE_000000007773090'),
}
BASE = 'https://www.data.go.kr'
OUT = os.path.join('data', 'raw')


def main():
    os.makedirs(OUT, exist_ok=True)
    s = requests.Session()
    for ym, (reg, atch) in FILES.items():
        path = os.path.join(OUT, f'nps_{ym}.csv')
        if os.path.exists(path):
            print(f'{path} 이미 있음 - 건너뜀')
            continue
        chk = s.post(f'{BASE}/cmm/cmm/check-limit.json',
                     data={'atchFileId': atch, 'fileDetailSn': 1}).json()
        if chk.get('needCaptcha'):
            print('포털이 보안문자 입력을 요구합니다. 브라우저에서 직접 내려받아 주세요.')
            break
        r = s.get(f'{BASE}/cmm/cmm/fileDownload.do',
                  params={'atchFileId': atch, 'fileDetailSn': 1}, stream=True)
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        print(f'{ym} (포털 등록 {reg}) → {path}')


if __name__ == '__main__':
    main()
