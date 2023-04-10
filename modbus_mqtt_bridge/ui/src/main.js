function registeredDeviceSelected(event, devices) {
    let serialIds = ['usb-selector-list', 'usb-slave-address-input-hide', 'usb-poll-rate-input-hide'];
    let defaultIds = serialIds;
    if (Object.keys(devices.find(e => e.unique_id === event.target.value) ?? {}).includes("serial")) {
        serialIds.forEach(id => document.getElementById(id).style.display = 'block');
    }
    else {
        defaultIds.forEach(id => document.getElementById(id).style.display = 'none');
    }
}

async function loadRegisteredDevices(devicesInfo) {
    document.getElementById('devices-table').getElementsByTagName('tbody')[0].innerHTML = "";
    const devices = await (await fetch(document.location.pathname + "/api/monitor/devices")).json();
    for (let i = 0; i < devices.length; i++) {
        const device = devices[i];
        const lastItem = devices.length === i + 1;
        let deviceInfo = devicesInfo.find(e => e.unique_id === device.device_id);
        var template = document.createElement('template');
        template.innerHTML = `<tr class="bg-white ${lastItem ? "" : "border-b "}dark:bg-gray-800 dark:border-gray-700">
            <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                ${deviceInfo.name}
            </th>
            <td class="px-6 py-4">
                ${deviceInfo.company_name}
            </td>
            <td class="px-6 py-4">
                ${deviceInfo.product_name}
            </td>
            <td class="px-6 py-4">
                ${device?.serial_port ? 'usb' : 'ip'}
            </td>
            <td class="px-6 py-4">
                ${device.serial_port}
            </td>
            <td class="px-6 py-4">
                ${device.slave_address}
            </td>
            <td class="px-6 py-4">
                ${device.poll_rate}
            </td>
            <td class="px-6 py-4">
                <svg id="${device.unique_id}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 cursor-pointer">
                    <path id="${device.unique_id}" stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
            </td>
        </tr>`.trim();
        template.content.firstChild.getElementsByTagName('svg')[0].addEventListener('click', async (event) => {
            await fetch(document.location.pathname + "/api/monitor/devices/" + event.target.id, {
                method: 'DELETE'
            });
            loadRegisteredDevices(devicesInfo);
        });
        document.getElementById('devices-table').getElementsByTagName('tbody')[0].appendChild(template.content.firstChild);
    }

}


async function addDeviceToRegistery(devices) {
    if (document.getElementById('add-device-form').checkValidity()) {
        if (true) { // CHECK HERE IF IT IS USB DEVICE (tbd only usb supported for now)
            await fetch(document.location.pathname + "/api/monitor/devices", {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "device_id": document.getElementById('devices-list').value,
                    "poll_rate": Number(document.getElementById('usb-poll-rate-input').value),
                    "serial_port": document.getElementById('usb-selector-list').value,
                    "slave_address": Number(document.getElementById('usb-slave-address-input').value)
                })
            });
        }
        loadRegisteredDevices(devices);
    }
}


async function loadSerialPorts() {
    const serialPorts = await (await fetch(document.location.pathname + "/api/serial")).json();
    serialPorts.forEach((device) => {
        const option = document.createElement("option");
        option.innerText = device;
        option.value = device;
        document.getElementById('usb-selector-list').appendChild(option);
    });
}

// Load available devices
(async() => {
    const devices = await (await fetch(document.location.pathname + "/api/devices")).json();
    devices.forEach((device) => {
        const option = document.createElement("option");
        const name = device.name + " - " + device.company_name + " " + device.product_name;
        option.innerText = name;
        option.value = device.unique_id;
        document.getElementById('devices-list').appendChild(option);
    });
    await loadRegisteredDevices(devices);
    document.getElementById('add-devices-btn').addEventListener('click', () => addDeviceToRegistery(devices));
    document.getElementById('devices-list').addEventListener("change", (event) => registeredDeviceSelected(event, devices));
})();

loadSerialPorts();

// tbd: implement testing/add-new-device tab
// document.getElementById('devices-tab').addEventListener('click', () => {
//     document.getElementById('test-input').style.display = 'none';
//     document.getElementById('devices-tab-content').style.display = 'block';
// });
// document.getElementById('register-tab').addEventListener('click', () => {
//     document.getElementById('test-input').style.display = 'block';
//     document.getElementById('devices-tab-content').style.display = 'none';
// });
// document.getElementById('testing').addEventListener('click', () => {
//     if (document.documentElement.classList.length == 1) {
//         document.documentElement.classList = [];
//         return;
//     }
//     document.documentElement.classList.add('dark');
// });
