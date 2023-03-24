import ApiRequestUtils from "./api_request_utils.js";
import { debounce } from "./utils.js";

let limit = 10
let current_user_page = 1;
const urlUsersApi = '/api/users'
const urlGivePermissionApi = '/api/givePermission'
const urlRevokePermissionApi = '/api/revokePermission'
const urlMachinesApi = '/api/machines'
const urlProfile = '/profile'
const urlManage = '/manage'


let table_input, machine_input, select_all, tbody, table_page, machines
let ARU = new ApiRequestUtils()

const params = new Proxy(new URLSearchParams(window.location.search), {
	get: (searchParams, prop) => searchParams.get(prop),
});

function givePermissionHandler(e) {
	e.preventDefault();
	const formData = new FormData(e.target)
	let params = getSelectedUsers(formData)

	let info = e.target.getElementsByClassName('modal-response-info')[0]
	info.style.display = 'block'

	ARU.post(urlGivePermissionApi, params).then(
		json => {
			if ('success' in json && json.success) {
				info.classList.add('info-success')
				info.innerText = 'Пользователям успешно выданы права'
				e.target.reset()
				getUsers()
				return
			}
			if ('warn' in json) {
				info.innerText += json.warn_msg
			}
			info.classList.add('info-error')
			info.innerText = `Неизвестный ответ от сервера, сообщите администратору: ${json}`
		},
		error_json => {
			if ('error' in error_json) {
				info.classList.add('info-error')
				info.innerText = `Неудалось выдать права. Код: ${error_json.error}, причина: ${error_json.error_msg}`
			}
		})
}


function revokePermissionHandler(e) {
	e.preventDefault();
	const formData = new FormData(e.target)
	let params = getSelectedUsers(formData)

	let info = e.target.getElementsByClassName('modal-response-info')[0]
	info.style.display = 'block'

	ARU.post(urlRevokePermissionApi, params).then(
		json => {
			if ('success' in json && json.success) {
				info.classList.add('info-success')
				info.innerText = `У пользователей успешно забраны права`
				e.target.reset()
				getUsers(table_input.value)
				return
			}
			if ('warn' in json) {
				info.innerText += json.warn_msg
			}
			info.classList.add('info-error')
			info.innerText = `Неизвестный ответ от сервера, сообщите администратору: ${json}`
		},
		error_json => {
			if ('error' in error_json) {
				info.classList.add('info-error')
				info.innerText = `Неудалось забрать права. Код: ${error_json.error}, причина: ${error_json.error_msg}`
			}
		})
}

function getSelectedUsers(formData) {
	let params = new URLSearchParams()
	formData.forEach((value, key) => (params.append(key, value)))

	for (const input of tbody.getElementsByTagName('input')) {
		if (input.type == 'checkbox' && input.name == 'user_select' && input.checked) {
			params.append('user', input.value)
		}
	}
	return params
}

function getUserHandler(json) {
	tbody.innerHTML = ''
	if (Object.keys(json.users).length == 0) {
		tbody.innerHTML = 'Пользователи не найдены'
		createPages(1, 1)
		return
	}

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
		return
	}
	if (max_page <= 7) {
		for (let i = 1; i <= max_page; i++) {
			createSpan(current_page, i)
		}
		return
	}

	let pages = getVisiblePages(current_page, max_page, 5)
	for (const element of pages) {
		if (element == '...') {
			table_page.append('...')
		} else {
			createSpan(current_page, element)
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
			getUsers(table_input.value, e.target.innerText)
		})
	}
	table_page.appendChild(span)
}

function createRow(key, obj) {
	let td = document.createElement("td")

	let input1 = document.createElement("input")
	input1.type = 'checkbox'
	input1.name = 'user_select'
	input1.value = key
	input1.setAttribute('aria-label', 'Выбрать пользователя ' + obj['fullname'])
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
	let data = obj['data']
	a3.innerText = data
	if (data.length === 0) {
		a3.innerText = 'Отсутствуют'
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
	a.addEventListener('click', e => {
		limit = Number(e.target.innerText)
		for (const obj of limit_spans) {
			if (obj.innerText == limit) {
				obj.classList.add('selected')
			} else {
				obj.classList.remove('selected')
			}
		}
		getUsers(table_input.value)
	})
}

function getUsers(query = '', page = current_user_page) {
	ARU.post(urlUsersApi, ARU.databaseParams(query, limit, page)).then(getUserHandler)
}

function getMachines(query = '') {
	ARU.post(urlMachinesApi, ARU.databaseParams(query, 20, 1)).then(getMachineHandler)
}

function getMachineHandler(json) {
	console.debug(json)
	machines.innerHTML = ''
	if (Object.keys(json.machines).length == 0) {
		return
	}
	for (let key in json.machines) {
		let option = document.createElement('option')
		option.innerText = key
		machines.appendChild(option)
	}
}

document.addEventListener("DOMContentLoaded", () => {

	table_input = document.getElementById('table-search-input')
	machine_input = document.getElementById('give-permission-machine-input')
	machines = document.getElementById('machines')
	tbody = document.getElementById('table-body')

	table_page = document.getElementById('table-page')
	select_all = document.getElementById('select-all')

	document.getElementById('give-permission-form').addEventListener('submit', givePermissionHandler);
	document.getElementById('revoke-permission-form').addEventListener('submit', revokePermissionHandler);


	let limit_spans = document.getElementById('table-limit').getElementsByTagName('a')
	for (const obj of limit_spans) {
		limitButtonHandler(obj, limit_spans)
	}

	select_all.addEventListener('click', e => {
		for (const input of document.getElementsByTagName('input')) {
			if (input.type == 'checkbox') {
				input.checked = e.target.checked
			}
		}
	})

	if (params.query != null) {
		table_input.value = params.query
	}

	let debouncedGetUsers = debounce(getUsers, 500);
	table_input.addEventListener('input', () => {
		debouncedGetUsers(table_input.value)
	})
	document.getElementById('table-search-button').addEventListener('click', () => {
		debouncedGetUsers(table_input.value)
	})
	machine_input.addEventListener('input', debounce((e) => {
		getMachines(e.target.value)
	}, 500))
	getUsers(table_input.value)
	setTimeout(getMachines, 500)
	// databaseUtils.get(urlMachinesApi + 1, '', 10, 1).then(json => {
	// 	console.log(json)
	// })


})