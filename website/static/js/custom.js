function process(data)
{
    alert("Surname(s) from JSON results: " + Object.keys(data).map(function(k) {return data[k]}));
};

var index = document.location.hash.indexOf('lang=');
if (index != -1)
{
    document.write('<div style=\"position: absolute; top: 5px; right: 5px;\">Chosen language: <b>' + decodeURIComponent(document.location.hash.substring(index + 5)) + '</b></div>');
}

function check() {
    var password_confirm = document.getElementById('password_confirm');
    console.log(password_confirm.value);
    var password = document.getElementById('password');
    console.log(password.value);
    if (password_confirm.value != password.value) {
        password_confirm.setCustomValidity('Password Must be Matching.');
    } else {
        // input is valid -- reset the error message
        password_confirm.setCustomValidity('');
    }
}

function deletepost(postId){
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/blog");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {{
        if (xhr.status === 200) {
                    alert('Post deleted successfully!');
                    // Redirect to another page or update UI as needed
                    window.location.href = "/blog";
                } else {
                    alert('Error deleting post!');
                }
    }};
    var data = JSON.stringify({ 'post_id': postId });
    xhr.send(data);
}

function deleteFile(imageId) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/upload");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {{
        if (xhr.status === 200) {
                    alert('File deleted successfully!');
                    // Redirect to another page or update UI as needed
                    window.location.href = "/upload";
                } else {
                    alert('Error deleting post!');
                }
    }};
    var data = JSON.stringify({ 'file_id': imageId });
    xhr.send(data);
}


function deleteUser(userId) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/admin");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {{
        if (xhr.status === 200) {
                    alert('User deleted successfully!');
                    // Redirect to another page or update UI as needed
                    window.location.href = "/admin";
                } else {
                    alert('Error deleting post!');
                }
    }};
    var data = JSON.stringify({ 'user_id': userId });
    xhr.send(data);
}

function deleteComment(comment_id,blog_id) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/comment");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {{
        if (xhr.status === 200) {
                    alert('Comment deleted successfully!');
                    // Redirect to another page or update UI as needed
                    console.log(blog_id)
                    window.location.href = "/blog/" + blog_id;
                } else {
                    alert('Error deleting post!');
                }
    }};
    var data = JSON.stringify({ 'comment_id': comment_id });
    xhr.send(data);
}

function filterFilesByDirectory() {
    const directoryFilter = document.getElementById("directory-filter");
    const selectedDirectory = directoryFilter.value;
    const fileTableBody = document.getElementById("file-table-body");
    const tableRows = fileTableBody.getElementsByTagName("tr");

    for (let i = 0; i < tableRows.length; i++) {
        const row = tableRows[i];
        const directoryCell = row.getElementsByTagName("td")[2];
        const directoryName = directoryCell.textContent.trim().substring(1); // Remove leading slash
        row.style.display = selectedDirectory === "" || selectedDirectory === directoryName ? "" : "none";
    }
}

function confirmDeleteUser(userId) {
    var confirmDelete = confirm("Are you sure you want to delete this user?");

    if (confirmDelete) {
      // User confirmed deletion, perform the deletion action
      deleteUser(userId);
    }
  }

function confirmDeleteFile(fileId) {
    var confirmDelete = confirm("Are you sure you want to delete this file?");

    if (confirmDelete) {
      // User confirmed deletion, perform the deletion action
      deleteFile(fileId);
    }
  }

