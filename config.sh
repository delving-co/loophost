gcloud compute instances \
    create-with-container sish \
    --zone="us-west2-a" \
    --tags="sish" \
    --metadata=ssh-keys="`curl https://github.com/joshuamckenty.keys`" \
    --container-mount-host-path="host-path=/mnt/stateful_partition/sish/ssl,mount-path=/ssl" \
    --container-mount-host-path="host-path=/mnt/stateful_partition/sish/keys,mount-path=/keys" \
    --container-mount-host-path="host-path=/mnt/stateful_partition/sish/pubkeys,mount-path=/pubkeys" \
    --container-image="antoniomika/sish:latest" \
    --machine-type="e2-micro" \
    --container-arg="--domain=fling.team" \
    --container-arg="--ssh-address=:2222" \
    --container-arg="--http-address=:80" \
    --container-arg="--https-address=:443" \
    --container-arg="--https=true" \
    --container-arg="--https-certificate-directory=/ssl" \
    --container-arg="--authentication-password=\"\"" \
    --container-arg="--authentication=true" \
    --container-arg="--authentication-keys-directory=/pubkeys" \
    --container-arg="--private-keys-directory=/keys" \
    --container-arg="--bind-any-host=false" \
    --container-arg="--bind-random-ports=false" \
    --container-arg="--bind-random-subdomains=false" \
    --container-arg="--bind-random-aliases=false" \
    --container-arg="--force-requested-aliases=true" \
    --container-arg="--force-requested-ports=true" \
    --container-arg="--force-requested-subdomains=true" \
    --container-arg="--tcp-aliases=true" \
    --container-arg="--service-console=true" \
    --container-arg="--log-to-client=true" \
    --container-arg="--admin-console=true" \
    --container-arg="--verify-dns=true" \
    --container-arg="--append-user-to-subdomain=true" \
    --container-arg="--append-user-to-subdomain-separator=." \
    --container-arg="--verify-ssl=false" \
    --container-arg="--https-ondemand-certificate=true" \
    --container-arg="--https-ondemand-certificate-accept-terms=true" \
    --container-arg="--https-ondemand-certificate-email=jmckenty@gmail.com" \
    --container-arg="--idle-connection=false" \
    --container-arg="--ping-client-timeout=2m" \
    --address="34.102.104.118"


ssh -p 2222 -R poet:443:localhost:443 joshuamckenty.fling.team
    --container-arg="--domain=fling.team" \
    --container-arg="--bind-hosts=joshuamckenty.fling.team,anoukruhaak.fling.team" \


Indirection for sharding of bounce hosts
