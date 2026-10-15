import { withApi, ok } from './_lib/http.js';
import { serverConfig } from './_lib/config.js';
import { storageMode } from './_lib/store.js';

export default withApi(async (_req, res) => {
  ok(res, {
    service: 'personal-info-butler',
    storage: storageMode(),
    llmReady: Boolean(serverConfig.llm.key),
    llmModel: serverConfig.llm.model,
    tokenRequired: Boolean(serverConfig.appToken),
  });
});
