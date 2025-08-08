// TaskFlowPro 主要 JavaScript 文件

$(document).ready(function () {
    // 自动隐藏消息提示
    setTimeout(function () {
        $('.alert').fadeOut('slow');
    }, 5000);

    // 表单验证增强
    $('form').on('submit', function () {
        var submitBtn = $(this).find('button[type="submit"]');
        var originalText = submitBtn.text();

        // 显示加载状态
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="loading"></span> 处理中...');

        // 5秒后恢复按钮状态（防止无限加载）
        setTimeout(function () {
            submitBtn.prop('disabled', false);
            submitBtn.text(originalText);
        }, 5000);
    });

    // 确认删除对话框
    $('.btn-delete').on('click', function (e) {
        if (!confirm('确定要删除这个项目吗？此操作不可撤销。')) {
            e.preventDefault();
        }
    });

    // 工具提示初始化
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 下拉菜单增强
    $('.dropdown-toggle').dropdown();
});

// 通用 AJAX 请求函数
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    $.ajax({
        url: url,
        method: method,
        data: data,
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function (response) {
            if (successCallback) {
                successCallback(response);
            }
        },
        error: function (xhr, status, error) {
            if (errorCallback) {
                errorCallback(xhr, status, error);
            } else {
                console.error('AJAX 请求失败:', error);
            }
        }
    });
}

// 显示消息提示
function showMessage(message, type) {
    var alertClass = 'alert-' + (type || 'info');
    var alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // 插入到页面顶部
    $('.container').first().prepend(alertHtml);

    // 自动隐藏
    setTimeout(function () {
        $('.alert').fadeOut('slow');
    }, 5000);
}

// 格式化日期
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 防抖函数
function debounce(func, wait) {
    var timeout;
    return function executedFunction() {
        var later = function () {
            clearTimeout(timeout);
            func();
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
} 