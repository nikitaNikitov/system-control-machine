

function openModal() {
	const id = this.getAttribute('data-modal');
	const modal = document.getElementById(id);
	modal.style.display = 'block';
}

function closeModal() {
	const id = this.getAttribute('data-modal');
	const modal = document.getElementById(id);
	modal.style.display = 'none';
}

window.addEventListener("DOMContentLoaded", function () {
	let openButtons = this.document.getElementsByClassName('open-modal')
	for (const button of openButtons) {
		button.onclick = openModal
	}

	let closeButtons = this.document.getElementsByClassName('close-modal')
	for (const button of closeButtons) {
		button.onclick = closeModal
	}
}, false);
window.onclick = function (event) {
	let isModal = (' ' + event.target.className + ' ').indexOf(' modal ') > -1;
	if (isModal) {
		event.target.style.display = "none";
		let info = event.target.getElementsByClassName('modal-response-info');
		if (info.length > 0) {
			info[0].className = 'modal-response-info'
			info[0].style.display = "none";
		}
	}
}