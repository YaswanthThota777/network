document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-link').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            document.getElementById(`content-${postId}`).style.display = 'none';
            document.getElementById(`edit-form-${postId}`).style.display = 'block';
        });
    });

    document.querySelectorAll('[id^=save-button-]').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const content = document.getElementById(`edit-content-${postId}`).value;

            fetch(`/edit_post/${postId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: `content=${encodeURIComponent(content)}`,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`content-${postId}`).textContent = data.new_content;
                    document.getElementById(`content-${postId}`).style.display = 'block';
                    document.getElementById(`edit-form-${postId}`).style.display = 'none';
                } else {
                    console.error('Failed to edit post.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    document.querySelectorAll('[id^=cancel-button-]').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            document.getElementById(`content-${postId}`).style.display = 'block';
            document.getElementById(`edit-form-${postId}`).style.display = 'none';
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const followButton = document.getElementById('follow');
    const followersCountElement = document.getElementById('followers');

    if (followButton) {
        followButton.addEventListener('click', function() {
            const isFollowing = followButton.dataset.following === 'true';
            const username = followButton.dataset.username;

            fetch(`/follow/${username}/`, {
                method: isFollowing ? 'DELETE' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle follow status
                    const newFollowingStatus = !isFollowing;
                    followButton.dataset.following = newFollowingStatus ? 'true' : 'false';
                    followButton.textContent = newFollowingStatus ? 'Unfollow' : 'Follow';

                    // Update followers count based on server response
                    const newFollowersCount = data.followers_count;
                    
                    // Update the DOM
                    followersCountElement.textContent = `Followers: ${newFollowersCount}`;
                    followersCountElement.dataset.followers = newFollowersCount;
                } else {
                    console.error('Failed to update follow status.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const commentLinks = document.querySelectorAll('.comment-link');

    commentLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const postId = this.dataset.postId;
            const commentSection = document.getElementById(`comment-section-${postId}`);

            if (commentSection.style.display === 'none' || commentSection.style.display === '') {
                commentSection.style.display = 'block';
            } else {
                commentSection.style.display = 'none';
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const liked = this.dataset.liked === 'true';

            fetch(`/toggle_like/${postId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the like button's text and data attributes
                    this.dataset.liked = data.liked;
                    this.innerHTML = `&#10084; ${data.likes_count}`;
                } else {
                    console.error('Failed to toggle like.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; cookies.length > i; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
