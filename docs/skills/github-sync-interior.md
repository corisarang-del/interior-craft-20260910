# Interior Craft Session Workflow (excerpt)

Same session-isolation rule. Never mix with Hanbang or electric-engineer repos.

- Remote: `https://github.com/corisarang-del/interior-craft-20260910`
- Local: `/var/minis/workspace/interior-craft-git`, branch `main`
- Working tree (volatile): `/var/minis/workspace/interior-craft/`
- Vault: `/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사/`
- Do not commit original videos, frames, or sungandang PDFs. Notes + images + metadata/docs/tests/scripts only.
- 정답 표기 상태는 원본 메타데이터 계약을 따른다: 화면 근거=확정, 직접 풀이=추론, 근거 없음=미확정.
- `기출핵심요약`은 `build_summary.py`로 회차·문항별 정답을 자동 매칭하며, 생성 후 답줄 100/100·누락 0과 관련 테스트를 확인한다.
- 원격 반영 전 `git status --short`와 최근 커밋을 확인하고 `main` push 후 상태를 다시 확인한다. 토큰은 출력하지 않는다.
- Next session: new repo + new local path. This repo is reference only.
