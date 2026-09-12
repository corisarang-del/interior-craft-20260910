# 실내건축기능사 필기 복원 워크플로우

Generated: 2026-09-10
Scope: 2017~2026 필기만. 실기·기사·산업기사 제외.

## Goal
공개 복원 소스(유튜브 나합격 클래스 + 성안당 자료실 PDF)로
Obsidian `지식/실내건축기능사/` 회차 노트와 핵심요약 100을 만든다.

## Vault
- `/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사/`
- 회차 노트: `기출문제/<회차>.md`
- 이미지: `기출문제/이미지/<회차>/qNN.jpg` (상대경로 `이미지/<회차>/qNN.jpg`)
- 핵심요약: `기출핵심요약/실내건축기능사.md`
- MOC: `_moc/실내건축기능사-MOC.md`

## Workspace (volatile)
- `/var/minis/workspace/interior-craft/`
- Git은 세션 전용 새 저장소. 전기기사·한방봇 저장소에 섞지 않는다.

## Question numbering
- 필기 60문항. 키는 전역 `"1"`~`"60"`.
- `sorted([k for k in q if k.isdigit()], key=int)` 순회. `q.get("1")` 루프 금지.
- 기본 `num_range = (1, 60)`.
- 제목 범위 정규식: `\d{2,3}[~-]\d{2,3}`
- 정답 상한: `answers[:60]`
- 미확정은 임의 생성 금지 (`정답: 미확정`, `image_confirmed: false`)

## Subjects (큐넷 출제기준 우선, 나합격 이론 재생목록 교차)
1. 실내디자인 일반
2. 색채 및 인간공학
3. 건축재료
4. 건축시공
5. 건축구조

과목 구간이 공식 확인되기 전에는 전역 1~60만 사용한다.

## Sources
- YouTube playlist `PL4sOWzc2AfD3Y5dvbieSEar2Vl6GbXHkg` (나합격 클래스)
- 성안당 자료실 공개 복원 PDF 3개 (2026-1/2/3회). 신규 문항만일 수 있음.
- ComCBT `xe/d6`는 2016년까지. 2017~ 회차 원본 없음.
- 에듀채널 예상문제는 회차 원본으로 쓰지 않음.
- 소스 없는 회차는 빈 노트를 만들지 않고 inventory에 `source=none`.

## YouTube pipeline
1. yt-dlp `--impersonate chrome --extractor-args "youtube:player_client=android"`
2. crv scene 0.30 + fps-floor 2.0 + max-frames 150
3. 나합격 복원 화면: 좌상단 큰 숫자(01~60) + 우측 Solution. 전기기사 하단 `N 번` 배지 아님
4. OCR 좌측 본문 3배 psm 4. 번호는 선두 토큰. `1)` 보기·`42 | Solution` 패널은 거절, `04 Solution`·`1 7` 공백 두자리는 번호
5. 빈 번호는 좌상 숫자 ROI(psm 8, whitelist 0-9)로만 보강
5. SequenceMatcher > 0.55 그룹화
6. 배지 단조 경로 + 지문 키워드 + 마진 90초. 반복 화면은 60→1 역방향
7. 4배 lanczos + unsharp
8. 자막 정답 패턴은 적고 정확하게. "N번이" 오탐 금지
9. 회차 문항 수 검증 후 노트 1회 생성. 워처 중간본 금지
10. 수동 보강 후 assign 재실행 금지
11. items.json 없이 키만 재매핑 금지
12. 이미지 문법 `![](상대경로)` 만. wiki embed 금지
13. OCR 원문을 노트 본문에 넣지 않음
14. 2편 영상은 한 회차로 병합

## Sungandang PDF
- 자료실 공개 파일만.
- 본문에 "신규 출제 문제를 제외한 문항은 교재"면 `restore_scope=new_only`.
- pdftotext -layout. 하단 가로 보기면 텍스트 보기 보강.
- 정답 없으면 미확정.

## Frequency summary
- 지문 정규화 `[^가-힣0-9]` 제거
- SequenceMatcher > 0.6 클러스터는 후보 생성용일 뿐, 같은 유형 확정 기준이 아님
- 점수 = 출제연도수×3 + 횟수 + 키워드×2, 2024~2026 가중 1.5
- 이미지 재판독으로 핵심 개념·질문 의도·풀이법을 교차 확인하고, 다른 유형은 분리
- 파일명·노트 번호·화면 좌상단 실제 번호가 다르면 해당 문항을 반복유형 링크에서 제외
- 전면검수 후 자격 전체 상위 100을 다시 계산. 반복유형과 단독출제를 구분해 표시
- 자격 전체 상위 100. 과목당 100 아님
- 대표는 텍스트 우선, 없으면 이미지

## Git
- 새 세션 저장소만. `git add .` 금지. 토큰 출력 금지.
- notes / images / metadata / docs / tests / scripts
- 원본 영상·frames는 커밋하지 않음
