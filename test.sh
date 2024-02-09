TEST='["terragrunt/account1/region1"]'
# For handling different TEST cases, ensure to replace the TEST variable value with the desired JSON string.
STG_AND_PROD=$(echo $TEST | jq -r '.[]')
for folder in $STG_AND_PROD; do
  # Check if the path includes 'env-staging' or 'env-production'
  if echo "$folder" | grep -q "env-staging"; then
    echo "STAGING_FOLDERS=$folder" >> $GITHUB_OUTPUT
  elif echo "$folder" | grep -q "env-production"; then
    echo "PRODUCTION_FOLDERS=$folder" >> $GITHUB_OUTPUT
  # For paths without explicit 'env-staging' or 'env-production', assume based on account
  elif echo "$folder" | grep -q "account2"; then
    # Assuming account2 without explicit env to be staging
    echo "STAGING_FOLDERS=$folder" >> $GITHUB_OUTPUT
  elif echo "$folder" | grep -q "account1"; then
    # Assuming account1 without explicit env to be production
    echo "PRODUCTION_FOLDERS=$folder" >> $GITHUB_OUTPUT
  fi
done
