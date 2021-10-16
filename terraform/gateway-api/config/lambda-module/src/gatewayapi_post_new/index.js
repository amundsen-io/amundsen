"use strict";

const axios = require("axios");

const BACKEND_INGRESS_URL = process.env.BACKEND_INGRESS_URL;

exports.handler = async (event) => {
	let [name, message] = ["", ""];

	if (event.queryStringParameters) {
		name = event.queryStringParameters.name;
		message = event.queryStringParameters.message;
	} else if (event.body) {
		const reqBody = JSON.parse(event.body);

		name = reqBody.name;
		message = reqBody.message;
	} else {
		return {
			statusCode: 400,
			headers: {
				"Content-Type": "text/html; charset=utf-8"
			},
			body: "<p>Invalid request format.</p>"
		};
	}

	try {
		await axios.post(`${BACKEND_INGRESS_URL}/new-post/?name=${name}&message=${message}`);

		return {
			statusCode: 200,
			headers: {
				"Content-Type": "text/html; charset=utf-8"
			},
			body: "<p>Message received!</p>"
		};
	} catch (err) {
		return {
			statusCode: 400,
			headers: {
				"Content-Type": "text/html; charset=utf-8"
			},
			body: "<p>Error</p>"
		};
	}
};
