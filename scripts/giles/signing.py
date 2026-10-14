"""Create/import the persistent personal code-signing identity in a dedicated keychain."""
from pathlib import Path
import argparse
import base64
import json
import os
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--github', action='store_true')
    args = parser.parse_args()
    folder = ROOT / '.giles-signing'
    folder.mkdir(mode=0o700, exist_ok=True)
    os.chmod(folder, 0o700)
    credentials = folder / 'credentials.json'
    if args.create and not credentials.exists():
        config = folder / 'openssl.cnf'
        config.write_text('[req]\ndistinguished_name=dn\nx509_extensions=code\nprompt=no\n[dn]\nCN=Giles Personal Code Signing\nO=Davy Burgevin\n[code]\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=critical,codeSigning\nsubjectKeyIdentifier=hash\n')
        data = {'password': secrets.token_urlsafe(32), 'keychainPassword': secrets.token_urlsafe(32)}
        run('/usr/bin/openssl', 'req', '-new', '-x509', '-newkey', 'rsa:3072', '-nodes', '-days', '3650', '-config', str(config), '-keyout', str(folder/'key.pem'), '-out', str(folder/'certificate.pem'))
        env = dict(os.environ, GILES_P12_PASSWORD=data['password'])
        subprocess.run(['/usr/bin/openssl', 'pkcs12', '-export', '-inkey', str(folder/'key.pem'), '-in', str(folder/'certificate.pem'), '-name', 'Giles Personal Code Signing', '-out', str(folder/'giles.p12'), '-passout', 'env:GILES_P12_PASSWORD'], env=env, check=True, capture_output=True)
        credentials.write_text(json.dumps(data))
    if os.environ.get('GILES_CERTIFICATE_P12'):
        (folder/'giles.p12').write_bytes(base64.b64decode(os.environ['GILES_CERTIFICATE_P12']))
        credentials.write_text(json.dumps({'password':os.environ['GILES_CERTIFICATE_PASSWORD'], 'keychainPassword':secrets.token_urlsafe(32)}))
        run('/usr/bin/openssl', 'pkcs12', '-in', str(folder/'giles.p12'), '-clcerts', '-nokeys', '-passin', 'pass:'+os.environ['GILES_CERTIFICATE_PASSWORD'], '-out', str(folder/'certificate.pem'))
    data = json.loads(credentials.read_text())
    keychain = folder/'giles.keychain-db'
    if not keychain.exists():
        run('/usr/bin/security', 'create-keychain', '-p', data['keychainPassword'], str(keychain))
    run('/usr/bin/security', 'unlock-keychain', '-p', data['keychainPassword'], str(keychain))
    run('/usr/bin/security', 'set-keychain-settings', '-lut', '21600', str(keychain))
    run('/usr/bin/security', 'import', str(folder/'giles.p12'), '-k', str(keychain), '-P', data['password'], '-T', '/usr/bin/codesign', '-T', '/usr/bin/security')
    run('/usr/bin/security', 'set-key-partition-list', '-S', 'apple-tool:,apple:,codesign:', '-s', '-k', data['keychainPassword'], str(keychain))
    fingerprint = subprocess.check_output(['/usr/bin/openssl','x509','-in',str(folder/'certificate.pem'),'-noout','-fingerprint','-sha1'],text=True).strip().split('=')[1].replace(':','')
    environment = {'GILES_SIGNING_KEYCHAIN':str(keychain), 'GILES_SIGNING_FINGERPRINT':fingerprint}
    (folder/'environment.json').write_text(json.dumps(environment))
    for p in folder.iterdir():
        if p.is_file():os.chmod(p,0o600)
    if os.environ.get('GITHUB_ENV'):
        with open(os.environ['GITHUB_ENV'],'a') as output:
            for k,v in environment.items():output.write(f'{k}={v}\n')
    if args.github:
        for name,value in {'GILES_CERTIFICATE_P12':base64.b64encode((folder/'giles.p12').read_bytes()).decode(),'GILES_CERTIFICATE_PASSWORD':data['password']}.items():
            subprocess.run(['gh','secret','set',name,'--repo','davyburgevin/giles'],input=value,text=True,check=True,stdout=subprocess.DEVNULL)
    print('Giles personal signing identity is ready; private material stays ignored.')


if __name__ == '__main__':
    main()
