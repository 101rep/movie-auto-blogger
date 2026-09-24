/**
 * Post Action Handlers Module
 * Handles preview, draft sync, immediate publish, and deletion of posts asynchronously.
 */
(function(window) {
  'use strict';

  const postActions = {
    async sendDraft(postId) {
      if (!confirm("이 글을 워드프레스 초안(Draft)으로 전송하시겠습니까?")) return;
      try {
        const res = await fetch(`/admin/api/send-draft/${postId}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
          alert(`초안 전송 완료! (WP ID: ${data.remote_post_id})`);
          window.location.reload();
        } else {
          alert(`전송 실패: ${data.error_message || "알 수 없는 오류"}`);
        }
      } catch (err) {
        alert("요청 중 통신 오류: " + err.message);
      }
    },

    async publishNow(postId) {
      if (!confirm("주의: 이 글을 워드프레스에 즉시 공개 발행(Publish)하시겠습니까?")) return;
      try {
        const res = await fetch(`/admin/api/publish-now/${postId}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
          alert(`즉시 발행 완료! (WP ID: ${data.remote_post_id})`);
          window.location.reload();
        } else {
          alert(`발행 실패: ${data.error_message || "알 수 없는 오류"}`);
        }
      } catch (err) {
        alert("요청 중 통신 오류: " + err.message);
      }
    },

    async deletePost(postId) {
      if (!confirm("게시글을 로컬 데이터베이스에서 삭제하시겠습니까? (워드프레스 원격 글은 삭제되지 않습니다)")) return;
      try {
        const res = await fetch(`/admin/api/delete-post/${postId}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
          alert(data.message || "삭제되었습니다.");
          window.location.reload();
        } else {
          alert("삭제 실패: " + (data.error_message || "알 수 없는 오류"));
        }
      } catch (err) {
        alert("삭제 요청 중 오류: " + err.message);
      }
    }
  };

  // Expose to window
  window.postActions = postActions;

  // Backward compatibility
  window.sendDraft = postActions.sendDraft;
  window.publishNow = postActions.publishNow;
  window.deletePost = postActions.deletePost;

})(window);
