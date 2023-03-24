import { getCookie } from './utils.js';

export default class ApiRequestUtils {
	constructor() {
		this.request = new XMLHttpRequest()
	}

	get(url, params) {
		return new Promise((resolve, reject) => {
			this.request.open("GET", url + '?' + params);

			this.request.onload = () => {
				if (this.request.status !== 200) {
					if (this.request.status === 403) {
						reject({ error: 0, error_msg: 'Нету доступа к данному адресу' })
						return
					}

					if (this.request.status === 404) {
						reject({ error: 0, error_msg: 'Такого адреса несуществует' })
						return
					}

					reject({ error: 0, error_msg: 'Отсутствует соединение с сайтом' })
					return
				}

				let json = JSON.parse(this.request.responseText)
				if ('error' in json) {
					reject(json)
				}
				resolve(json)
			}
			this.request.send()
		})
	}

	post(url, params) {
		return new Promise((resolve, reject) => {
			this.request.open("POST", url);
			this.request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			this.request.setRequestHeader("Content-Type", 'application/x-www-form-urlencoded');
			this.request.onload = () => {
				console.log(this.request)
				if (this.request.status !== 200) {
					if (this.request.status === 403) {
						reject({ error: 0, error_msg: 'Нету доступа к данному адресу' })
						return
					}

					if (this.request.status === 404) {
						reject({ error: 0, error_msg: 'Такого адреса несуществует' })
						return
					}

					reject({ error: 0, error_msg: 'Отсутствует соединение с сайтом' })
					return
				}

				let json = JSON.parse(this.request.responseText)
				if ('error' in json) {
					reject(json)
				}
				resolve(json)
			}
			this.request.send(params)
		})
	}

	databaseParams(query = '', limit = 10, page = 1) {
		return new URLSearchParams({
			query: query,
			limit: limit,
			list: page,
		}).toString()
	}
	fromJson(params) {
		return new URLSearchParams(params).toString()
	}

}