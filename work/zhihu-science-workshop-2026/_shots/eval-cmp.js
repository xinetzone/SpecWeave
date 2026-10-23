document.getElementById('runCmp').click();
await new Promise(function (r) { setTimeout(r, 2600); });
return {
  table: document.getElementById('cmpBody').innerText.replace(/\s+/g, ' '),
  conclusion: document.getElementById('cmpConclusion').textContent
};
