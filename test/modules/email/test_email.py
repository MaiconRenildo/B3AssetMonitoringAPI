from api.modules import email

def test_should_send_email():
    assert email.send(
      msg="Olá, Maicon!\n\nSua conta foi confirmada!",
      subject="Confirmação de conta",
      to="maicon.renildo1@gmail.com",
    ) == {}
