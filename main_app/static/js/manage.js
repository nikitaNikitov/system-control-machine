let isBusy = false;
let limit = 10
let current_user_page = 1;
const urlResponse = '/api/users'
const urlProfile = '/profile'
const urlManage = '/manage'


let input, select_all, tbody, table_page

const params = new Proxy(new URLSearchParams(window.location.search), {
	get: (searchParams, prop) => searchParams.get(prop),
});



function handler() {
	if (this.status != 200) {
		console.warn(`Выдался код: ${this.status}`)
	}
	let json = JSON.parse(this.responseText)

	if ('error' in json) {
		console.error(`Ошибка: ${json}`)
		// TODO Обработка ошибок
		return
	}

	tbody.innerHTML = ''
	console.log(json)
	for (let key in json.users) {
		let obj = json.users[key]
		if (obj == undefined) {
			continue
		}
		createRow(key, obj)
	}
	createPages(json.current_page, json.max_pages)
}

function createPages(current_page, max_page) {
	table_page.innerHTML = ''
	if (max_page == 0) {
		createSpan(current_page, 1)
	} else if (max_page <= 7) {
		for (let i = 1; i <= max_page; i++) {
			createSpan(current_page, i)
		}
	} else {
		let pages = getVisiblePages(current_page, max_page, 5)
		console.log(pages)
		for (const element of pages) {
			if (element == '...') {
				table_page.append('...')
			} else {
				createSpan(current_page, element)
			}
		}
	}
}
function getVisiblePages(currentPage, pagesCount, showPages) {
	let fromPage = Math.max(currentPage - Math.floor(showPages / 2), 1);
	let toPage = Math.min(currentPage + Math.floor(showPages / 2), pagesCount);
	let size = toPage - fromPage + 1;
	let k = 0
	let atStart = fromPage == 1;
	let atEnd = toPage == pagesCount;
	if (!atStart)
		size += 2;
	if (!atEnd)
		size += 2;
	let result = [];
	if (!atStart) {
		result[0] = 1;
		result[1] = '...';
		k += 2;
	}
	if (!atEnd) {
		result[size - 2] = '...';
		result[size - 1] = pagesCount;
	}
	for (let i = fromPage; i <= toPage; i++)
		result[k++] = i;
	return result
}

function createSpan(current_page, i) {
	let span = document.createElement("span")
	span.innerText = i
	if (current_page == i) {
		span.classList.add('selected')
	} else {
		span.addEventListener('click', e => {
			console.log(input.value + " " + e.target.innerText)
			getUsers(input.value, e.target.innerText)
		})
	}
	table_page.appendChild(span)
}

function createRow(key, obj) {
	let td = document.createElement("td")

	let input1 = document.createElement("input")
	input1.type = 'checkbox'
	input1.onclick = function () {
		if (!this.checked) {
			select_all.checked = false
		}
	}
	let tr = document.createElement("tr")
	let a1 = document.createElement("a")
	a1.innerText = obj['fullname']
	a1.href = urlProfile + '/' + key
	let a2 = document.createElement("a")
	a2.innerText = obj['group']
	a2.href = urlManage + '?query=' + obj['group']
	let a3 = document.createElement("a")
	let data = JSON.stringify(obj['data'])
	if (data.length <= 2) {
		a3.innerText = 'Отсутствуют'
	} else {
		a3.innerText = 'Показать'
		a3.setAttribute('data-jsondata', data)
		a3.addEventListener('click', e => {
			let json = e.target.getAttribute('data-jsondata')
			console.log(json)
		})
	}

	tr.appendChild(td.cloneNode()).appendChild(input1)
	tr.appendChild(td.cloneNode()).appendChild(a1)
	tr.appendChild(td.cloneNode()).appendChild(a2)
	tr.appendChild(td.cloneNode()).appendChild(a3)
	tbody.appendChild(tr)
}

function limitButtonHandler(a, limit_spans) {
	if (a.innerText == limit) {
		a.className = 'selected'
	}
	console.log(a)
	a.addEventListener('click', e => {
		limit = Number(e.target.innerText)
		for (const obj of limit_spans) {
			if (obj.innerText == limit) {
				obj.classList.add('selected')
			} else {
				obj.classList.remove('selected')
			}
		}
		console.log(input.value + " " + e.target.innerText)
		getUsers(input.value)
	})
}

function getUsers(query = '', page = current_user_page) {
	if (isBusy) {
		return
	}
	isBusy = true;
	setTimeout(() => isBusy = false, 200)
	current_user_page = page
	if (query.length != 0) {
		xmlHttp.open("GET", `${urlResponse}?query=${query}&limit=${limit}&list=${page}`);
	} else {
		xmlHttp.open("GET", `${urlResponse}?limit=${limit}&list=${page}`);
	}
	xmlHttp.send();
}

const xmlHttp = new XMLHttpRequest();
xmlHttp.onload = handler

document.addEventListener("DOMContentLoaded", () => {

	input = document.getElementById('table-search-input')
	tbody = document.getElementById('table-body')

	table_page = document.getElementById('table-page')

	let limit_spans = document.getElementById('table-limit').getElementsByTagName('a')
	for (const obj of limit_spans) {
		limitButtonHandler(obj, limit_spans)
	}

	select_all = document.getElementById('select-all')
	select_all.addEventListener('click', e => {
		for (const input of document.getElementsByTagName('input')) {
			if (input.type == 'checkbox') {
				input.checked = e.target.checked
			}
		}
	})

	input = document.getElementById('table-search-input')
	if (params.query != null) {
		input.value = params.query
	}
	input.addEventListener('change', e => {
		// TODO поменять 'test' на выбор прав по станкам
		getUsers(input.value)
	})
	document.getElementById('table-search-button').addEventListener('click', e => {
		getUsers(input.value)
	})
	getUsers(input.value)
})