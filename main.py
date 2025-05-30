import asyncio
from datetime import datetime, timezone
import logging

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus
import websockets

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(Action.boot_notification)
    def on_boot_notification(
        self,
        charge_point_vendor: str,
        charge_point_model: str,
        **kwargs
    ):
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )


async def on_connect(websocket):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request.headers[
            "Sec-WebSocket-Protocol"
        ]
    except KeyError:
        logging.error(
            "Client hasn't requested any Subprotocol. "
            "Closing Connection"
        )
        return await websocket.close()
    if websocket.subprotocol:
        logging.info(
            f"Protocols Matched: "
            f"{websocket.subprotocol}"
        )
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            f"Protocols Mismatched | Expected Subprotocols: "
            f"{websocket.available_subprotocols},"
            f" but client supports  {requested_protocols} | "
            f"Closing connection"
        )
        return await websocket.close()

    charge_point_id = websocket.request.path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect, "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"]
    )

    logging.info(
        "Server Started listening to new connections..."
    )
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())