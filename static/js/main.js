document.querySelectorAll('.reactions').forEach(block => {
    const newsId = block.dataset.news;
    const likeBtn = block.querySelector('.like-btn');
    const dislikeBtn = block.querySelector('.dislike-btn');
    const likeCount = block.querySelector('.like-count');
    const dislikeCount = block.querySelector('.dislike-count');

    function updateButtons(userAction) {
        likeBtn.classList.toggle('active', userAction === 'like');
        dislikeBtn.classList.toggle('active', userAction === 'dislike');
    }

    async function sendReaction(action) {
        const resp = await fetch(`/react/${newsId}/${action}`);
        const data = await resp.json();
        if (resp.ok) {
            likeCount.textContent = data.likes;
            dislikeCount.textContent = data.dislikes;
            updateButtons(data.user_action);
        }
    }

    likeBtn.addEventListener('click', () => sendReaction('like'));
    dislikeBtn.addEventListener('click', () => sendReaction('dislike'));
});