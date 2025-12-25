document.addEventListener('DOMContentLoaded', function() {
    const favButtons = document.querySelectorAll('.favorite-btn');

    favButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const reportId = this.dataset.id;
            const icon = this.querySelector('i');
            fetch(`/favorite/${reportId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.liked === 1) {
                    icon.classList.remove('bi-star');
                    icon.classList.add('bi-star-fill');
                } else {
                    icon.classList.remove('bi-star-fill');
                    icon.classList.add('bi-star');
                }
            })
            .catch(err => console.error(err));
        });
    });
});