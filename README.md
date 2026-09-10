# 실내건축기능사 필기 복원 (2017~2026)

세션 전용 작업 저장소. 전기기사·한방봇 저장소와 분리.

## 볼트
`/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사/`

## 현재 상태 (2026-09-11)
- 유튜브 나합격 클래스 공개 회차 13개 노트 생성 (742문항 / 이미지 697, MD5 중복 0)
- 핵심요약 100: OCR 클러스터 + 2024~ 1.5배 가중
- 성안당 2026-1/2/3회 PDF: 자료실 비회원 차단. `raw/sungandang/`에 드롭하면 `pdf_parse.py`로 파싱
- 공개 소스 없는 회차(거의 모든 2회, 2025-2/3)는 빈 노트 안 만듦

## 화면 레이아웃 (나합격 클래스)
전기기사 하단 `N 번` 배지가 아님. 좌상단 큰 숫자 `01`~`60` + 우측 Solution 패널.

## 실행
```
python3 tests/test_inventory.py
python3 scripts/run_round.py 2024-1회
python3 scripts/build_moc.py
python3 scripts/build_summary.py
```
