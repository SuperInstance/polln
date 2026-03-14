import ZAI from 'z-ai-web-dev-sdk';

async function readGEM() {
  try {
    const zai = await ZAI.create();

    const result = await zai.functions.invoke('page_reader', {
      url: 'https://github.com/NVlabs/GEM'
    });

    console.log('Title:', result.data.title);
    console.log('URL:', result.data.url);
    console.log('Content:', result.data.html?.substring(0, 10000));
    
    return result.data;
  } catch (error) {
    console.error('Error:', error);
  }
}

readGEM();
