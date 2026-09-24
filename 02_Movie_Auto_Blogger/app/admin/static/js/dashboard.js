/**
 * Dashboard Client Actions Module
 * Provides asynchronous API integrations for the system dashboard.
 */
(function(window) {
  'use strict';

  const dashboardActions = {
    async testMovieApi() {
      const btn = document.getElementById("btnTestMovieApi");
      const originalHtml = btn ? btn.innerHTML : "";
      if (btn) {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> 확인 중...';
        btn.disabled = true;
      }
      try {
        const res = await fetch("/admin/api/test-movie-api", { method: "POST" });
        const data = await res.json();
        alert(data.message || (data.success ? "연결 성공" : "연결 실패"));
      } catch (err) {
        alert("연결 테스트 요청 중 통신 오류: " + err.message);
      } finally {
        if (btn) {
          btn.innerHTML = originalHtml;
          btn.disabled = false;
        }
      }
    },

    async testAiApi(provider) {
      try {
        const res = await fetch(`/admin/api/test-${provider}`, { method: "POST" });
        const data = await res.json();
        alert(`[${provider.toUpperCase()}] ` + (data.message || (data.success ? "연결 성공" : "연결 실패")));
      } catch (err) {
        alert(`[${provider.toUpperCase()}] 연결 확인 중 오류: ` + err.message);
      }
    },

    async testWordPressApi() {
      const btn = document.getElementById("btnTestWp");
      let originalHtml = "";
      if (btn) {
        originalHtml = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> 확인 중...';
        btn.disabled = true;
      }
      try {
        const res = await fetch("/admin/api/test-wordpress", { method: "POST" });
        const data = await res.json();
        if (data.success) {
          alert(`[워드프레스 연결 성공]\n사이트: ${data.site_url || "연결됨"}\n사용자: ${data.user || "인증완료"}`);
        } else {
          alert(`[워드프레스 연결 확인 결과]\n${data.message || "연결 실패"}`);
        }
      } catch (err) {
        alert("워드프레스 연결 테스트 중 통신 오류: " + err.message);
      } finally {
        if (btn) {
          btn.innerHTML = originalHtml;
          btn.disabled = false;
        }
      }
    },

    async triggerAutomation(vertical = 'ALL') {
      let confirmMsg = "";
      if (vertical === 'MOVIE') {
        confirmMsg = "🎬 [영화 블로그 (트렌드스팟24)]\n자동화 파이프라인(4편 수집 -> AI 작성 -> 품질 검사 -> 워드프레스 예약)을 지금 즉시 실행하시겠습니까?";
      } else if (vertical === 'TRAVEL') {
        confirmMsg = "✈️ [여행 블로그 (트래블픽24)]\n자동화 파이프라인(4개 도시 코스 가이드 -> 고유 사진 매칭 -> 워드프레스 예약)을 지금 즉시 실행하시겠습니까?";
      } else {
        confirmMsg = "🚀 [전체 일괄 실행 (영화 + 여행)]\n영화 블로그와 여행 블로그의 자동화 파이프라인을 모두 가동하여 총 8개 포스팅을 즉시 예약하시겠습니까?";
      }

      if (!confirm(confirmMsg)) return;

      const triggerBtn = document.getElementById("triggerAutoDropdown");
      let originalText = "";
      if (triggerBtn) {
        originalText = triggerBtn.innerHTML;
        triggerBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> 실행 중...';
        triggerBtn.disabled = true;
      }

      try {
        const res = await fetch(`/admin/api/trigger-automation?vertical=${vertical}`, { method: "POST" });
        const data = await res.json();
        alert(`[자동화 실행 완료]\n` +
              `대상: ${data.vertical || vertical}\n` +
              `결과: ${data.success ? "성공" : "확인 필요"}\n` +
              `생성: ${data.generated_count || 0}건 | 예약: ${data.scheduled_count || 0}건 | 실패: ${data.failed_count || 0}건\n\n` +
              `[상세 요약]\n${data.summary || "완료되었습니다."}`);
        window.location.reload();
      } catch (err) {
        alert("자동화 실행 요청 중 오류: " + err.message);
      } finally {
        if (triggerBtn) {
          triggerBtn.innerHTML = originalText;
          triggerBtn.disabled = false;
        }
      }
    },

    async toggleAutomation() {
      try {
        const res = await fetch("/admin/api/toggle-automation", { method: "POST" });
        const data = await res.json();
        alert(data.message || (data.auto_publish ? "자동화가 켜졌습니다." : "자동화가 꺼졌습니다."));
        window.location.reload();
      } catch (err) {
        alert("토글 요청 중 오류: " + err.message);
      }
    }
  };

  // Expose to window for inline onclick attributes and global calls
  window.dashboardActions = dashboardActions;

  // Backward compatibility for legacy inline onclicks
  window.testMovieApi = dashboardActions.testMovieApi;
  window.testAiApi = dashboardActions.testAiApi;
  window.testWordPressApi = dashboardActions.testWordPressApi;
  window.triggerAutomation = dashboardActions.triggerAutomation;
  window.toggleAutomation = dashboardActions.toggleAutomation;

})(window);
