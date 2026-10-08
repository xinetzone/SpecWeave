/* travel-planner 前端交互：确认弹窗（毛玻璃 dialog）、忙碌遮罩、对话框开关 */
(function () {
  "use strict";

  var confirmDialog = document.getElementById("confirm-dialog");
  var confirmMessage = document.getElementById("confirm-message");
  var confirmOk = document.getElementById("confirm-ok");
  var pendingForm = null;

  // 删除等危险操作：拦截提交，先弹确认
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.dataset.confirm) return;
    event.preventDefault();
    pendingForm = form;
    if (confirmMessage) confirmMessage.textContent = form.dataset.confirm;
    if (confirmDialog) confirmDialog.showModal();
  });

  if (confirmOk) {
    confirmOk.addEventListener("click", function () {
      if (confirmDialog) confirmDialog.close();
      if (pendingForm) {
        pendingForm.dataset.confirm = ""; // 避免二次拦截
        pendingForm.requestSubmit();
        pendingForm = null;
      }
    });
  }

  // 弹窗关闭按钮
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-close]");
    if (btn) {
      var dlg = btn.closest("dialog");
      if (dlg) dlg.close();
    }
    var opener = event.target.closest("[data-dialog]");
    if (opener) {
      var target = document.getElementById(opener.dataset.dialog);
      if (target && typeof target.showModal === "function") target.showModal();
    }
  });

  // 长耗时表单（导入校验、AI 生成）：提交后显示忙碌遮罩
  var busy = document.getElementById("busy");
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (form instanceof HTMLFormElement && form.dataset.loading !== undefined && busy) {
      busy.classList.remove("hidden");
    }
  });
})();
