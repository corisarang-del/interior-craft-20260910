# 실내건축기능사 필기 복원 (2017~2026)

세션 전용 작업 저장소. 전기기사·한방봇 저장소와 분리.

## 볼트
`/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사/`

## 현재 상태 (2026-09-10)
- 테스트: inventory/assign/answers/notes/frequency/pdf_parse/ocr_frames/fill_gaps
- 2025-1회 PoC: 57/60 문항 이미지 노트. 누락 23·51·59 (해당 화면이 영상에 없음)
- 성안당 2026-1/2/3회 PDF: 자료실 비회원 다운로드 차단. `raw/sungandang/`에 파일 드롭 필요
- 유튜브 나머지 회차: inventory.json의 youtube 라운드, `scripts/run_round.py`

## 화면 레이아웃 (나합격 클래스)
전기기사 하단 `N 번` 배지가 아님. 좌상단 큰 숫자 `01`~`60` + 우측 Solution 패널.

## 실행
```
python3 tests/test_inventory.py
python3 scripts/run_poc_2025_1.py
python3 scripts/run_round.py 2024-1회
python3 scripts/build_moc.py
```
