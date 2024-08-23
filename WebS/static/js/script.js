// Đợi cho khi tài liệu đã sẵn sàng
document.addEventListener("DOMContentLoaded", function() {
    // Lắng nghe sự kiện cuộn chuột
    window.addEventListener("scroll", function() {
        var navbar = document.querySelector(".navbar");
        // Thêm class navbar-scrolled nếu cuộn xuống đủ đến vị trí của navbar
        if (window.scrollY > navbar.offsetHeight) {
            navbar.classList.add("navbar-scrolled");
        } else {
            // Xoá class navbar-scrolled nếu cuộn lên trên đầu trang
            navbar.classList.remove("navbar-scrolled");
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Xử lý cho modal sửa
    $('#editModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var studentId = button.data('id');
        var studentName = button.data('name');
        var studentClass = button.data('class');
        var studentAchievement = button.data('achievement');
        var studentBirthday = button.data('ngay_sinh')

        var modal = $(this);
        modal.find('#editStudentId').val(studentId);
        modal.find('#editName').val(studentName);
        modal.find('#editClass').val(studentClass);
        modal.find('#editAchievement').val(studentAchievement);
        modal.find('#editBirthday').val(studentBirthday);
        modal.find('form').attr('action', '/edit_student/' + studentId);
    });

    // Xử lý cho modal xóa
    $('#deleteModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var studentId = button.data('id');
        var className = button.data('class');

        var modal = $(this);
        modal.find('#deleteStudentId').text(studentId);
        modal.find('#deleteStudentIdInput').val(studentId);
        modal.find('#deleteClassNameInput').val(className);
    });
});

