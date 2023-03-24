import ApiRequestUtils from "./api_request_utils.js";
import { debounce } from "./utils.js";


let limit = 10
let current_machine_page = 1;
const urlMachinesApi = '/api/machines'
const urlAddMachineApi = '/api/addMachine'
const urlDeleteMachinesApi = '/api/deleteMachine'




let table_input, select_all, tbody, table_page, create_machine_form
let ARU = new ApiRequestUtils()

const params = new Proxy(new URLSearchParams(window.location.search), {
	get: (searchParams, prop) => searchParams.get(prop),
});


function getMachineHandler(json) {
	tbody.innerHTML = ''
	if (Object.keys(json.machines).length == 0) {
		tbody.innerHTML = 'Станки не найдены'
		createPages(1, 1)
		return
	}

	for (let key in json.machines) {
		let obj = json.machines[key]
		if (obj == undefined) {
			continue
		}
		createRow(key, obj)
	}
	createPages(json.current_page, json.max_pages)
}

function createMachineHandler(e) {
	e.preventDefault();
	const formData = new FormData(e.target)
	let params = new URLSearchParams()
	formData.forEach((value, key) => (params.append(key, value)))

	let info = e.target.getElementsByClassName('modal-response-info')[0]
	info.style.display = 'block'

	ARU.post(urlAddMachineApi, params).then(
		json => {
			if ('success' in json && json.success) {
				info.classList.add('info-success')
				info.innerText = `Станок '${params.get('machine_id')}' успешно добавлен!`
				e.target.reset()
				getMachines(table_input.value)
				return
			}
			info.classList.add('info-error')
			info.innerText = `Неизвестный ответ от сервера, сообщите администратору: ${json}`
		},
		error_json => {
			if ('error' in error_json) {
				info.classList.add('info-error')
				info.innerText = `Неудалось добавить станок '${params.machine_id}'. Код: ${error_json.error}, причина: ${error_json.error_msg}`
			}
		})
}

function deleteMachinesHandler(e) {
	let params = new URLSearchParams()
	for (const input of tbody.getElementsByTagName('input')) {
		if (input.type == 'checkbox' && input.name == 'machine_select' && input.checked) {
			params.append('machine', input.value)
		}
	}
	if (params.length == 0) {
		return
	}
	console.log(e.target)
	let info = e.target.parentElement.getElementsByClassName('modal-response-info')[0]
	info.style.display = 'block'

	ARU.get(urlDeleteMachinesApi, params).then(
		json => {
			if ('success' in json && json.success) {
				info.classList.add('info-success')
				info.innerText = `Станки успешно удалены!`
				getMachines(table_input.value)
				return
			}
			info.classList.add('info-error')
			info.innerText = `Неизвестный ответ от сервера, сообщите администратору: ${json}`
		},
		error_json => {
			if ('error' in error_json) {
				info.classList.add('info-error')
				info.innerText = `Неудалось удалить станки. Код: ${error_json.error}, причина: ${error_json.error_msg}`
			}
		}
	)
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
	let tr = document.createElement("tr")

	let input1 = document.createElement("input")
	input1.type = 'checkbox'
	input1.name = 'machine_select'
	input1.value = key
	input1.setAttribute('aria-label', 'Выбрать станок ' + key)
	input1.onclick = function () {
		if (!this.checked) {
			select_all.checked = false
		}
	}

	tr.appendChild(td.cloneNode()).appendChild(input1)
	tr.appendChild(td.cloneNode()).innerText = key
	tr.appendChild(td.cloneNode()).innerText = obj.short_name
	tr.appendChild(td.cloneNode()).innerText = obj.description
	tr.addEventListener('click', e => {
		// TODO Создать открытие модали с информацией о станке и возможностью перегенерировать токен
	})
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
		getMachines(table_input.value)
	})
}

function getMachines(query = '', page = current_machine_page) {
	ARU.get(urlMachinesApi, ARU.databaseParams(query, limit, page)).then(getMachineHandler)
}

document.addEventListener("DOMContentLoaded", () => {

	table_input = document.getElementById('table-search-input')
	tbody = document.getElementById('table-body')
	select_all = document.getElementById('select-all')
	table_page = document.getElementById('table-page')

	document.getElementById('create-machine-form').addEventListener('submit', createMachineHandler);
	document.getElementById('delete-machines-button').addEventListener('click', deleteMachinesHandler)

	let limit_spans = document.getElementById('table-limit').getElementsByTagName('a')
	for (const obj of limit_spans) {
		limitButtonHandler(obj, limit_spans)
	}

	select_all.addEventListener('click', e => {
		for (const input of tbody.getElementsByTagName('input')) {
			if (input.type == 'checkbox') {
				input.checked = e.target.checked
			}
		}
	})

	if (params.query != null) {
		table_input.value = params.query
	}

	let debouncedGetMachines = debounce(getMachines, 500);
	table_input.addEventListener('input', () => {
		debouncedGetMachines(table_input.value)
	})
	document.getElementById('table-search-button').addEventListener('click', () => {
		debouncedGetMachines(table_input.value)
	})
	getMachines(table_input.value)

	// databaseUtils.get(urlMachinesApi + 1, '', 10, 1).then(json => {
	// 	console.log(json)
	// })


})