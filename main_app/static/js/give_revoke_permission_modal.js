import ApiRequestUtils from "./api_request_utils.js";
import { debounce } from "./utils.js";

const urlGivePermissionApi = '/api/givePermission'
const urlRevokePermissionApi = '/api/revokePermission'
const urlMachinesApi = '/api/machines'


let table_input, machine_input, select_all, tbody, table_page, machines
let ARU = new ApiRequestUtils()

const params = new Proxy(new URLSearchParams(window.location.search), {
	get: (searchParams, prop) => searchParams.get(prop),
});

function submitHandler(e) {
	e.preventDefault();
	const formData = new FormData(e.target)
	let params = new URLSearchParams()
	formData.forEach((value, key) => (params.append(key, value)))
	params.append('user', e.target.getAttribute('data-user'))
	return params
}

function givePermissionHandler(e) {
	let params = submitHandler(e)

	let info = e.target.getElementsByClassName('modal-response-info')[0]
	info.style.display = 'block'

	console.log(params)

	ARU.post(urlGivePermissionApi, params).then(
		json => {
			if ('success' in json && json.success) {
				info.classList.add('info-success')
				info.innerText = 'Пользователю успешно выдано право'
				e.target.reset()
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
	let params = submitHandler(e)

	let info = e.target.getElementsByClassName('modal-response-info')[0]
	info.style.display = 'block'

	console.log(params)

	ARU.post(urlRevokePermissionApi, params).then(
		json => {
			if ('success' in json && json.success) {
				info.classList.add('info-success')
				info.innerText = `У пользователя успешно забраны права`
				e.target.reset()
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
	machine_input = document.getElementById('give-permission-machine-input')
	machines = document.getElementById('machines')

	document.getElementById('give-permission-form').addEventListener('submit', givePermissionHandler);
	document.getElementById('revoke-permission-form').addEventListener('submit', revokePermissionHandler);

	machine_input.addEventListener('input', debounce((e) => {
		getMachines(e.target.value)
	}, 500))
	setTimeout(getMachines, 500)
})