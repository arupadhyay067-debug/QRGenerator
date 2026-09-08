from flask import Flask, render_template, request, send_file
import qrcode
import io
import base64

app = Flask(__name__)


@app.template_filter("b64encode")
def b64encode_filter(data):
    return base64.b64encode(data).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def index():
    qr_image = None
    error = None

    if request.method == "POST":
        link = request.form.get("link", "").strip()

        if not link:
            error = "Please enter a link."
        else:
            if not link.startswith(("http://", "https://")):
                link = "https://" + link

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )

            qr.add_data(link)
            qr.make(fit=True)

            image = qr.make_image(
                fill_color="black",
                back_color="white"
            )

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            qr_image = buffer.getvalue()

    return render_template(
        "index.html",
        qr_image=qr_image,
        error=error
    )


@app.route("/download", methods=["POST"])
def download():
    link = request.form.get("link", "").strip()

    if not link:
        return "No link provided", 400

    if not link.startswith(("http://", "https://")):
        link = "https://" + link

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )

    qr.add_data(link)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name="qrcode.png"
    )


if __name__ == "__main__":
    app.run(debug=True)